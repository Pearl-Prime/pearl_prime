# Visual Dialogue Systems in Manga
## Design Reference Document — Phoenix Omega Manga Pipeline

**Version:** 1.0  
**Date:** 2026-04-17  
**Author:** Pearl_Research  
**Purpose:** Comprehensive reference for implementing genre-accurate speech bubble rendering

---

## Overview

Manga dialogue is a visual language as much as a verbal one. Speech bubbles are not containers for text — they are expressive actors in the scene. Their shape, border treatment, tail style, and placement all communicate register, emotion, and speaker identity before a single word is read. This document catalogs the full visual grammar of manga dialogue across eleven major genres, with enough precision for programmatic implementation.

---

## 1. Shōnen (Dragon Ball, Naruto, One Piece, Demon Slayer)

### Bubble Shapes

| Shape | Usage | Frequency |
|-------|-------|-----------|
| **Round/Oval** | Normal speech, conversation | Very high — default shape |
| **Spiky/Jagged** | Shouts, power declarations, rage, battle cries | Very high — appears multiple times per action page |
| **Cloud/Rounded cloud** | Internal thoughts, doubt, quiet fear | Moderate |
| **Square/Rectangular** | Narration boxes for time/place; rare inner voice | Low |
| **Whisper** | Secret plans, aside comments, embarrassed confessions | Low to moderate |
| **Scream** | Ultra-jagged with thick border, often bleeds off panel | High in climactic moments |
| **Electronic/Robotic** | Villain machines, Den Den Mushi (transponder snails), radio | Moderate in tech-heavy arcs |
| **Drip/Horror** | Nearly absent; appears only in dark arcs (Pain arc, Muzan scenes) | Very rare |

**Shōnen-specific conventions:**
- Spiky bubbles scale with emotional intensity. A 4-point starburst for surprise; a 12-point full starburst for a power declaration.
- Bubbles frequently break the panel border in climactic moments — the speech literally cannot be contained.
- Demon Slayer favors slightly more rounded, decorative bubble borders with subtle texture compared to the clean stark lines of Dragon Ball.
- One Piece uses extremely oversized bubbles for Luffy's declarations, visually dominating the panel to represent his outsized personality.

### Tail Styles

- **Pointer tail (standard):** Dominant style. Short, sharp triangular tail pointing directly at speaker's mouth or general face region.
- **Curved tail:** Used in softer moments — Naruto's quiet talks with Iruka, Goku with Gohan.
- **Dotless/no-tail:** Thought bubbles and internal monologue; also used for voices heard in a character's memory.
- **Multiple tails:** Crowd cheering scenes, group battle cries ("Let's go!" from multiple fighters).
- **Broken/disconnected tail:** Off-panel shouts, characters calling from another room, radio communication.

Shōnen overwhelmingly favors the sharp pointer tail — it conveys directness and energy.

### Typography Conventions

- **Normal speech:** Medium-weight sans-serif, body size ~18-24pt equivalent in print.
- **Emphasis:** Bold weight, often with a slight size increase (1.2x). Applied to keywords, not full sentences.
- **Whisper:** Lighter weight, smaller size (0.7x), often italic equivalent in Japanese typesetting.
- **Scream:** ALL CAPS equivalent (in Japanese, this becomes kata-kana rendering or enlarged hiragana), maximum bold, 2-3x body size.
- **Handwritten fonts:** Used for SFX, villain characters with alien quality (Frieza's calm cruelty is sometimes rendered in slightly unusual font), ancient texts/prophecies.
- **Bold triggers:** A character's name when first revealed; a technique name on first use; a shocking revelation; the final word of a declaration ("I will become King of the Pirates!").
- **Line breaks:** Short lines preferred. Three lines maximum per bubble in action sequences; up to five in dialogue-heavy scenes.

### Text Direction

- **Horizontal:** Modern shōnen is almost entirely horizontal right-to-left reading.
- **Vertical:** Used for: ancient inscriptions, technique names rendered dramatically, some chapter titles, formal declarations in ceremonial context.

### Sound Effects (SFX/Onomatopoeia)

Shōnen SFX are treated as full visual elements — they occupy space, have weight, often fill the background.

**Three Japanese onomatopoeia categories:**
- **Giongo** (actual sounds): punches, explosions, footsteps
- **Giseigo** (living being sounds): voices, animal calls
- **Gitaigo** (states/textures, no actual sound): the shimmer of a blade, the silence of tension — these are uniquely Japanese and have no direct English equivalent

**Common shōnen SFX vocabulary:**
| Japanese | Romaji | Meaning/Use |
|----------|--------|-------------|
| ドン | DON | Impact, landing, dramatic reveal |
| ズン | ZUN | Heavy thud, sinking feeling |
| バキ | BAKI | Bone crack, hard impact |
| ドカ | DOKA | Punch connecting |
| ゴゴゴ | GOGOGO | Menacing aura, approaching power |
| シュ | SHU | Fast movement, slash |
| ズダダ | ZUDADA | Running at speed |
| ドドド | DODODO | Rumbling approach (Jojo-adjacent but present in shōnen) |
| カッ | KA | Flash of light, eye opening sharply |
| ピク | PIKU | Twitch, subtle reaction |
| ズキ | ZUKI | Sting of pain, emotional hurt |
| ハァ | HAA | Panting, exhaustion |
| ゴォォ | GOOO | Wind, energy aura building |
| バン | BAN | Door slam, explosive appearance |
| ドキ | DOKI | Heartbeat (emotional moment) |

SFX placement: typically integrated into the action, large enough to read from across a page, colored/outlined separately from panel tones.

### Caption Boxes

- **Narrator:** Rare. Used for time jumps ("Three years later..."), location ("The Hidden Leaf Village"). Thin rectangular box, small neutral font.
- **Internal monologue:** Moderate use. Cloud bubble or no border — just text slightly offset from character.
- **Flashback:** Softer screentone borders, or inverted (white-on-black text boxes).
- Shōnen uses relatively few captions — the action speaks.

### Spatial Rules

- Reading order: right-to-left, top-to-bottom (within each panel).
- First speaker always upper-right.
- In two-person exchanges, bubbles alternate sides, creating a visual rhythm.
- Bubbles never cover the protagonist's face during key dramatic beats.
- During "power-up" pages (splash/full-page), bubbles are minimal or absent — the image must breathe.
- Maximum panel coverage: ~25% in action scenes, up to 40% in dialogue scenes.

---

## 2. Shōjo (Sailor Moon, Fruits Basket, Nana, CardCaptor Sakura)

### Bubble Shapes

| Shape | Usage | Notes |
|-------|-------|-------|
| **Round/Oval** | Standard conversation | Often with softer, sometimes hand-drawn border |
| **Floral/Decorative oval** | Tender emotional moments | Unique to shōjo — border has small flourishes |
| **Cloud** | Daydreams, fantasy, hopes | Very common; often elaborate multi-lobed cloud |
| **Square** | Narrator, internal reflection | More frequent than shōnen |
| **Borderless text** | Profound emotional thought, environmental voice | Very common in shōjo |
| **Whisper** | Dashed, soft, small — confessions, embarrassed speech | Very common |
| **Spiky** | Rare; only for genuine shock or argument | Much rarer than shōnen; less intense spikes |

**Shōjo-specific:** Bubbles are frequently softer, more organic in shape. Fruits Basket uses bubbles with slightly irregular, almost hand-drawn borders to suggest warmth and human imperfection. Nana contrasts this with cleaner, sharper bubbles for Nana Osaki (punk aesthetic) vs. rounder ones for Nana Komatsu (soft personality).

### Tail Styles

- **Curved/flowing tail:** Dominant. Soft S-curve or gentle arc toward speaker, reinforcing emotional warmth.
- **Pointer tail:** Present but less sharp than shōnen; more of a soft wedge.
- **Borderless/no-tail:** Very common for internal thought. Characters in shōjo often have extended internal monologue without bubbles at all — text simply floats in the panel's negative space.
- **Multiple tails:** Rarely needed; shōjo tends toward intimate two-person conversation.

### Typography Conventions

- **Normal:** Similar size to shōnen, but font choice tends toward slightly more rounded letterforms.
- **Emotional emphasis:** Italics (in Japanese typesetting, slightly slanted or stretched characters). Less reliance on ALL-CAPS.
- **Whisper:** Very small, lighter, often enclosed in a small cloud or simply smaller text in the same bubble.
- **Narration/internal:** Often stylistically distinct — different font weight, slightly italic, placed outside bubbles.
- **Handwritten fonts:** More common in shōjo for personal notes, letters, diary entries (Nana has multiple letter sequences).

### Text Direction

- Mostly horizontal.
- Vertical text appears in: dramatic emotional declarations, traditional ceremony (wedding scenes, formal settings), classical poetry/lyrics quoted by characters.
- CardCaptor Sakura uses vertical text for magical incantations.

### Sound Effects (SFX/Onomatopoeia)

Shōjo SFX are smaller, more delicate, and often integrated decoratively rather than dominating the panel.

**Common shōjo SFX:**
| Japanese | Romaji | Meaning |
|----------|--------|---------|
| ドキドキ | DOKIDOKI | Heart pounding (romance/anxiety) |
| ふわ | FUWA | Floating, dreamy sensation |
| きゅ | KYU | Heartache, squeezing of heart |
| ぽっ | PO | Blushing, warmth in cheeks |
| しーん | SHIIN | Deep silence |
| ぱっ | PA | Sudden brightness, spark of realization |
| はっ | HA | Sharp intake of breath, realization |
| ぼろ | BORO | Tears falling |
| ざわ | ZAWA | Crowd murmur, unease |
| にこ | NIKO | Smile |
| ぎゅ | GYU | Tight hug |
| ふふ | FUFU | Gentle laugh |
| くす | KUSU | Suppressed giggle |
| ぽた | POTA | Single teardrop |
| ときめき | TOKIMEKI | The flutter of romantic feeling |

### Caption Boxes

- Very common. Shōjo uses first-person narrator captions extensively.
- Internal thoughts are the dominant mode of storytelling — Fruits Basket and CardCaptor Sakura both have narrators that are the protagonist's inner voice.
- Flashback captions with soft edges, often with decorative floral corners.
- Time/place labels are rare; more often contextual ("That summer...").

### Spatial Rules

- Bubbles frequently placed within fields of screentone flowers, sparkles, or abstract patterns unique to shōjo.
- Negative space is intentional — large empty spaces are emotional beats, not wasted space.
- Multiple small bubbles can spiral around a character to show racing thoughts.
- Panels can be broken by bubbles in a decorative rather than energetic way.

---

## 3. Seinen (Berserk, Vagabond, Monster, Vinland Saga, Oyasumi Punpun)

### Bubble Shapes

| Shape | Usage | Notes |
|-------|-------|-------|
| **Round/Oval** | Conversation | Clean, minimal — very little decoration |
| **Square/Rectangular** | Narration — heavy use | Often without rounded corners; stark, authoritative |
| **Irregular/Organic** | Disturbed characters (Griffith's cold detachment, Johan's eerie calm) | Slightly off-standard to signal wrongness |
| **Borderless text** | Deep internal state, philosophical musing | Very common in seinen |
| **Whisper** | Intimate scenes, conspiracy | Present but understated |
| **Horror elements** | Berserk uses drip-adjacent bubbles for demonic speech | Contextual |

**Seinen convention:** Less visual ornamentation; the bubbles themselves are quieter and more architectural. In Vagabond, Inoue uses minimal bubble borders — the art is so dominant that bubbles feel like they're whispering around it.

### Tail Styles

- **Pointer tail:** Present; more architectural and less playful than shōnen.
- **Broken/disconnected tail:** Heavy use for narration and inner voice, both common in seinen.
- **No tail (borderless text):** Extremely common in philosophical monologue (Punpun's omniscient narrator "Uncle").
- Berserk uses multiple long narrow tails on bubble clusters during battlefield scenes.

### Typography Conventions

- **Normal:** Clear, readable, no-nonsense. Seinen privileges legibility over expression.
- **Emphasis:** Contextual. In Monster, Johan's lines are rarely bolded — his power comes from calm, measured speech. Contrast with normal characters who react with emphasized words.
- **Handwritten:** Relatively rare for speech; used for letters, notes, journals.
- **Narration:** Often a distinct, slightly smaller font in rectangular boxes.
- Oyasumi Punpun's narrator (the cosmic "voice") uses unusual boxed text that's visually different from all character dialogue.

### Sound Effects (SFX/Onomatopoeia)

Seinen SFX are more realistic in scale — large for Berserk's epic violence, smaller for psychological works.

**Common seinen SFX (Berserk/Vagabond style):**
| Japanese | Meaning |
|----------|---------|
| ドゴォ | Massive impact, Dragon Slayer connecting |
| ズシャ | Flesh tearing |
| ビュ | Fast draw, blade whistle |
| ゴォォ | Wind, fire roar |
| パキ | Bone snap |
| ドッ | Heavy fall |
| シャン | Metal ring, armor |
| ガキン | Sword clash |
| ズブ | Blade entering flesh |
| ガポ | Wet horrible sound |
| じわ | Spreading (blood, realization) |
| しん | Absolute silence (psychological works) |
| ざわ | Crowd unease |
| ざく | Footstep in grass/dirt |
| ぐい | Forceful grab |

### Caption Boxes

- **Very heavy use.** Seinen is the most caption-dense genre.
- Multiple caption boxes per page telling parallel stories (Monster cross-cuts between Johan and Tenma extensively).
- Vinland Saga uses caption boxes to deliver historical context mid-action.
- Oyasumi Punpun's narrator captions are a structural feature, not just labeling.

### Spatial Rules

- Seinen often allows longer text per bubble than other genres.
- Splash pages in Berserk are intentionally caption-free to let Miura's art dominate.
- Monster's psychological tension is partly created by panels with very few bubbles — silence is weaponized.

---

## 4. Josei (Honey and Clover, Nodame Cantabile, Princess Jellyfish, Chihayafuru)

### Bubble Shapes

Similar to shōjo but more restrained decoration. Round/oval dominant with clean borders. Whisper bubbles very common for awkward romantic tension. Square narration boxes used more freely than shōjo. Chihayafuru uses angular bubbles during competitive karuta scenes to signal intensity, softening in emotional scenes.

### Tail Styles

Curved tails dominate (emotional warmth); pointer tails for more direct statements. Borderless thought is common in moments of romantic confusion or artistic contemplation.

### Typography

Body size is proportionally moderate. Emphasis through italics/weight on emotional peaks. Nodame's musical exclamations ("GYABOO!") use oversized all-caps equivalent.

### SFX (Josei-specific)

| Japanese | Meaning |
|----------|---------|
| ドキ | Heartbeat |
| ぽっ | Blush |
| ぎゅ | Hug/squeeze |
| はあ | Sigh |
| もじ | Fidgeting |
| そわそわ | Restlessness |
| ずーん | Sinking depression |
| きゃあ | Shriek/excitement |
| じーん | Deeply moved |
| ぱちぱち | Applause |
| ぼ | Dazed expression |
| ふわ | Floaty feeling |
| にこ | Smile |
| ぼろぼろ | Crying heavily |
| ふっ | Small laugh, exhale |

### Caption Boxes

Heavy narrator presence. Honey and Clover is one of the most caption-dense manga — Takemoto's first-person narration runs parallel to dialogue. Chihayafuru uses captions for karuta card poem text (critical to the story).

---

## 5. Kodomomuke (Doraemon, Pokémon Adventures, Chi's Sweet Home)

### Bubble Shapes

All shapes rounder and softer than adult genres. Spiky bubbles exist but with fewer, more rounded spikes — surprise rather than rage. Cloud bubbles very common. No horror elements. Electronic bubbles present in Doraemon (gadget communication). Chi's Sweet Home uses a unique small, cute round bubble to match Chi's tiny voice.

### Typography

Larger font sizes for younger readers. Fewer words per bubble. Simpler vocabulary. Pokémon Adventures uses all-caps for Pokémon attack names as a convention.

### SFX

Large, cheerful, colorful SFX. Sound effects are designed to be readable and fun.

| Japanese | Meaning |
|----------|---------|
| ドカン | Explosion (cartoony) |
| ぴかぴか | Sparkling |
| もふもふ | Fluffy texture (Chi) |
| わいわい | Cheerful crowd noise |
| きらきら | Glittering |
| ぴょん | Bouncing jump |
| にゃ | Cat sound (Chi) |
| ばーん | Big reveal |
| どたばた | Running around chaotically |
| にこにこ | Happy smiling |
| ぼん | Poof/transformation |
| うきうき | Excited/bouncy feeling |
| くるくる | Spinning |
| てくてく | Gentle walking |
| ひらひら | Fluttering |

### Caption Boxes

Minimal. Young readers prefer dialogue over narration. Location labels present but simple.

---

## 6. Isekai (Re:Zero, Mushoku Tensei, Overlord, That Time I Got Reincarnated as a Slime)

### Bubble Shapes

Heavy use of **square/rectangular** boxes for status screens, system notifications, and skill descriptions — a genre-defining feature. Round/oval for conversation. Spiky for combat and surprise (very frequent in this genre). Electronic/digital bubbles for system messages, with sharp corners and often a different fill (light blue tint convention). Overlord uses unusually formal, angular bubbles for Ainz's undead authority.

**Isekai-specific:** The "game screen" caption box — essentially a status window rendered as a visual element with borders, labels, and sometimes tabular data. This is unique to isekai and must be a first-class bubble type in the Phoenix Omega system.

### Tail Styles

Standard pointer tail dominant. System/status messages have no tails — they float as interface elements.

### Typography

Romaji (Latin alphabet) mixed in for skill names. System text in monospace or tech-style font. Character speech in normal rounded font. Overlord uses deliberately archaic-feeling fonts for Ainz's villain speeches.

### SFX

Similar to shōnen with heavy action vocabulary, plus:

| Japanese | Meaning |
|----------|---------|
| ピコン | Status notification ping |
| ガシャン | Armor equip |
| レベルアップ | Level up (sometimes rendered as SFX) |
| ズシン | Heavy monster footstep |
| メキメキ | Transformation cracking |
| ビキビキ | Power building (vein-bulge) |
| ドロ | Slime movement (TenSura) |
| きゅぽん | Slime absorption |
| ガァァ | Monster roar |
| ドカドカ | Mass combat |
| ひゅ | Magic projectile |
| ズバン | Skill activation |
| ドーン | Dramatic reveal |
| カキーン | Critical hit |
| シュルル | Binding magic |

### Caption Boxes

Extremely heavy. Status screens, skill explanations, world-building lore boxes. Isekai has the highest caption density of any genre. Often multi-paragraph boxes requiring careful space management.

---

## 7. Horror (Junji Ito: Uzumaki, Tomie, Gyo; Hideout, Homunculus)

### Bubble Shapes

| Shape | Notes |
|-------|-------|
| **Round/Oval** | Normal speech — deliberately mundane to contrast with horror content |
| **Drip/Horror** | Ink appears to drip from bubble borders; used for cursed/supernatural speech |
| **Irregular organic** | Bubbles that look almost wrong, slightly too large or strangely placed |
| **Borderless text** | Horror protagonists' shock thoughts, floating uncomfortably in white space |
| **Whisper** | Very common — horror lives in whispered warnings no one heeds |
| **Scream** | Present but Ito often underplays screams — makes them more disturbing |

**Junji Ito's signature:** Most horror actually uses very normal, clean bubbles for speech. The horror is in the content and art, not the bubble design. This deliberate mundanity of the speech design against extraordinary visual horror is a key technique. Tomie's bubbles are perfectly normal while she says deeply wrong things.

However, for supernatural/cursed speech:
- Bubbles with irregular, slightly melting borders
- Text that seems too small or too large for its container
- Bubbles placed in uncomfortable locations (bottom of panel, partially off page)

### Tail Styles

Standard pointer tail. In supernatural moments: disconnected tails (voices from nowhere). No-tail for thoughts that feel like they might not be the character's own.

### Typography

Normal speech: absolutely standard. Horror convention is that normal-looking text saying horrible things is more frightening than obviously "horror-styled" text. Exception: cursed text, supernatural entities — these may use irregular spacing, mixed sizes, or unusual letterforms.

### SFX

Horror SFX are placed uneasily — too small, at wrong angles, in empty spaces. They unsettle rather than energize.

| Japanese | Meaning |
|----------|---------|
| じわじわ | Slowly spreading (decay, madness) |
| ぐにゃ | Twisting/warping |
| ぐちゃ | Wet, organic, horrible |
| めきめき | Something wrong breaking |
| ずるずる | Dragging/slithering |
| ぼこぼこ | Bubbling, lumpy |
| ひたひた | Quiet, pursuing footsteps |
| ぴちゃ | Wet drip |
| ずぶ | Sinking into something |
| ぎ | Creak |
| ゆらゆら | Swaying (spiral madness, Uzumaki) |
| ぶよぶよ | Gelatinous, wrong flesh |
| ぐるぐる | Spinning (spiral) |
| きい | High squeal |
| べたべた | Sticky, clinging |

### Caption Boxes

Junji Ito uses captions sparingly and effectively — typically only for time/place labels. When horror narration occurs, it is often in the protagonist's voice, rendered in standard boxes, describing increasingly abnormal things in increasingly normal language.

### Spatial Rules

Silence panels extremely common. Ito uses 3-4 panel sequences with no dialogue whatsoever, building dread. The spatial rule is: when the horror is about to appear, clear the text away.

---

## 8. Sports (Slam Dunk, Haikyuu!!, Blue Lock, Ashita no Joe, Yowamushi Pedal)

### Bubble Shapes

Similar to shōnen: round/oval dominant, spiky for competitive intensity, scream for game-winning moments. **Sports-specific:** Bubbles during play sequences are often minimal or absent — the motion lines and body positioning carry the information. Commentary boxes (announcer voice) use a distinctive rectangular format, sometimes with a microphone icon or source label.

**Haikyuu!! convention:** Small, efficient bubbles during rally sequences — short bursts of tactical communication. Pre-game and post-game scenes use longer, rounder bubbles for emotional content.

**Blue Lock innovation:** Interior monologue during play rendered as large irregular bubbles with fragmented text — representing the fractured flow of tactical thought in real-time.

### Typography

Clean sans-serif for normal speech. ALL-CAPS equivalents for performance calls ("MINE!", "SET!", "SPIKE!"). Commentary boxes in slightly different typeface.

### SFX

Sports SFX emphasize impact, speed, and crowd:

| Japanese | Meaning |
|----------|---------|
| バスッ | Ball impact/swish |
| ドリブル | Dribble sound |
| キュキュ | Shoe squeak on court |
| ズバン | Spike |
| ドスン | Body contact |
| バンッ | Ball against backboard |
| がっ | Catch/grab |
| ぴゅ | Fast serve |
| ドオォ | Crowd roar |
| かっ | Hard hit (baseball/tennis) |
| ぱしん | Ball into glove/palm |
| ビュン | Speed of throw |
| ずだだ | Running footsteps |
| ガッ | Collision |
| ドヨドヨ | Crowd murmur |

### Caption Boxes

Scoreboard captions (score, time, set number) as graphic elements. Announcer commentary boxes. Coach's tactical narration. Flashback training captions. Sports manga uses caption boxes structurally to convey match information.

---

## 9. Slice of Life / Iyashikei (Yotsuba&!, Barakamon, March Comes in Like a Lion, A Silent Voice)

### Bubble Shapes

Round/oval almost exclusively for speech. Cloud bubbles for gentle thought. Very few spiky bubbles — conflict is internalized, not explosive. Whisper bubbles extremely common for shy, uncertain characters (Rei in March, Shoya in A Silent Voice).

**Iyashikei-specific:** Bubbles have a gentle, organic quality. In Barakamon, Yanda and Seishuu's banter uses quick small bubbles that overlap and interrupt each other — rendering the energy of casual conversation.

**A Silent Voice** special case: Shoya's speech bubbles near people he fears have intentional spatial discomfort — placed awkwardly, sometimes partially cut off — representing social anxiety in visual form.

### Typography

Relaxed, warm. Yotsuba&! uses rounded friendly fonts. March Comes in Like a Lion uses introspective internal monologue in flowing text without strict bubble borders.

### SFX

Quiet, everyday SFX — the sound design of gentleness:

| Japanese | Meaning |
|----------|---------|
| さらさら | Flowing water, calligraphy brush |
| とことこ | Small quick footsteps (child, Yotsuba) |
| ふわ | Soft floating sensation |
| ごろごろ | Comfortable rolling around |
| もふもふ | Soft texture (animals) |
| ことこと | Cooking sounds |
| ぽかぽか | Warm, comfortable |
| ぱちぱち | Fire crackling |
| しとしと | Gentle rain |
| さくさく | Crisp stepping in leaves/snow |
| ぽたぽた | Drops falling |
| ちゃぽん | Water ripple |
| むしゃむしゃ | Eating contentedly |
| のびのび | Stretching out |
| ころころ | Rolling/tumbling (children, small things) |

### Caption Boxes

March Comes in Like a Lion is heavily captioned — Rei's inner narration is a primary storytelling mode. A Silent Voice uses visual silence over captions. Yotsuba&! has minimal captions — the world is shown, not explained.

### Spatial Rules

**Silence panels are central to the genre.** Iyashikei uses more silence panels per page than any other genre. The empty panel — or panel with only environment and no character speech — IS the emotional content.

---

## 10. BL/GL (Given, Bloom Into You, Saezuru Tori wa Habatakanai, Dungeon Meshi GL elements)

### Bubble Shapes

Shōjo-influenced rounded, soft bubbles. Whisper bubbles extremely frequent (confessions, intimate exchanges). Borderless thought very common — unspoken feeling rendered as floating text. Bloom Into You uses bubbles that break the panel edge during emotional peaks.

**BL-specific (Given, Saezuru):** Dramatic close-ups use minimal speech; bubbles retreat from panels where eyes or hands communicate the emotion. When bubbles do appear, they're often isolated — one small bubble in a large panel, giving the text enormous weight.

### SFX

Emotional vocabulary similar to shōjo (DOKIDOKI, PO, GYU) with additional:

| Japanese | Meaning |
|----------|---------|
| どきっ | Single sharp heartbeat |
| ぎゅっ | Tight hold |
| ふっ | Soft exhale |
| じん | Deep emotional warmth |
| つん | Prickling feeling in eyes before tears |
| ぽろ | Single tear |
| ざわ | Internal unease |
| かっ | Sudden flush |
| どきどき | Sustained heart racing |
| ふるふる | Trembling |
| めろ | Melting (emotional) |
| きゅん | Heart-squeeze |
| とく | Single heartbeat, recognition |
| しーん | Meaningful silence |
| ぴく | Involuntary reaction |

### Caption Boxes

First-person narration common. Internal emotional processing rendered as floating text. Given's Ritsuka and Mafuyu's chapters alternate internal narrator voice.

---

## 11. Mecha (Evangelion, Gundam: The Origin, Eureka Seven)

### Bubble Shapes

**Electronic/robotic bubbles** are a first-class bubble type. Communications between pilots use sharp-cornered, screen-like borders — often with a subtle line pattern suggesting a monitor or comms screen. Regular round/oval for human scenes. Square narration for military/tactical briefings.

**Evangelion-specific:** NERV briefings use a clinical rectangular format. Pilot communications inside Eva units use rounded but sharp-edged bubbles to suggest simultaneous human and machine context. Interior existential monologue — uniquely Evangelion — uses large borderless text floating in abstract backgrounds.

**Gundam: The Origin** uses formal, structured bubbles reflecting Yoshikazu Yasuhiko's old-school aesthetic. Military briefings have columnar text arrangement.

### Typography

Communications: monospace or technical font for robotic/system voice. Human speech: normal. In Evangelion's psychological sequences, text can become fragmented, isolated words drifting in white space.

### SFX

Mecha SFX combine action vocabulary with mechanical/technological sounds:

| Japanese | Meaning |
|----------|---------|
| ゴォン | Engine ignition, giant motor |
| ガシャン | Armor lock, mechanical connection |
| ビーン | Energy weapon charge |
| ドゴォン | Massive mecha impact |
| ガガガ | Mechanical grinding |
| ズン | Heavy mecha footfall |
| バキン | Structure breaking |
| ヴゥン | Electrical/energy hum |
| ドカカン | Explosion with debris |
| シュウ | Hydraulic hiss |
| ピピ | Alert beep |
| ゴゴゴ | Rumbling mecha movement |
| メキ | Metal stress |
| ズダン | Progressive cannon impact |
| ヴン | AT Field activation |

### Caption Boxes

Heavy in military planning sequences. Eureka Seven uses caption boxes for Renton's diary/journal, a defining structural element. Evangelion's "15 years since Second Impact" type captions are genre-standard scene-setting.

---

## Universal Spatial Rules Summary

| Rule | Detail |
|------|--------|
| Reading order | Right-to-left, top-to-bottom within each panel |
| First speaker | Upper-right position in panel |
| Tail pointing | Always toward speaker's mouth or face |
| Layering | Bubbles over background, under character foreground when possible |
| Max coverage | ~30% of panel area (reduce font/size if exceeded) |
| Silence convention | Action/climax/iyashikei: silence panels are structural, not accidental |
| Panel borders | High-intensity genres allow bubbles to break panel borders |
| Group scenes | Right-to-left sequencing; group shout = multiple tails on one bubble |
| Off-panel speech | Broken/disconnected tail pointing to panel edge |
| Minimum bubble size | Never smaller than readable (approximately 60×30px at target DPI) |

---

*End of Document 01 — Visual Dialogue Systems*
