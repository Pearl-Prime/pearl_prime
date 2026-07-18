# Vertical Webtoon Romance (Korean format) — Style Bible

Touchstones: *Lore Olympus* (Rachel Smythe), *True Beauty* (Yaongyi), *Cheese in the Trap* (Soonkki), *Love Advice from the Great Duke of Hell*, *I Love Yoo*, *Let's Play*, *Your Throne*.

## 1. Market + reader contract
Readers are 15–28, heavily mobile, reading in ~5-minute sessions during commutes/breaks on Webtoon, Lezhin, Kakao, Tapas. They expect *color*, *vertical scroll momentum*, *clear hook per episode*, *weekly schedule loyalty*, and *slow-burn romance with high-frequency small payoffs*. They will reject black-and-white pages, print-style panel grids, dense text, and slow episodes without a hook.

## 2. Visual grammar
- **Panel count per chapter ("episode"):** 60–120 panels over a vertical canvas roughly 800px × 10,000–15,000px. Panels are *separated by vertical whitespace*, not gridded.
- **Words per episode:** 200–450 (distributed across a long scroll; ~2–5 words per panel-view).
- **Silent-panel ratio:** 30–45%. Vertical scroll rhythm *needs* empty visual beats between dialogue panels.
- **Black-fill ratio:** Non-applicable in traditional sense — the lane is *full color*. Instead: "mood-field saturation" 0.4–0.9 (Lore Olympus's pink/blue color-coded emotional register).
- **Screentone density:** Zero (digital color painting replaces tone).
- **Spread frequency:** N/A. Instead: *megapanels* — tall, single-scene panels 1500–3000px tall — used 1–3× per episode for emotional peaks.
- **Reaction-shot frequency:** Very high — 6–12 per episode. The reaction shot IS the webtoon grammar; each swipe should deliver a face.
- **Line weight profile:** Variable; many Webtoons use colored lines rather than black. Soft digital brush is common; sharp pen-line signals either action or comedic beats.

## 3. Pacing + beat conventions
- **Chapter length:** Per episode: 40–80 "screens" on mobile. Weekly release cadence. Total series runs 100–400 episodes.
- **Chapter hook family:** *Swipe-bait open* — episode opens on a question the reader was left with last week, re-asked visually (a face, an unfinished text message, a hand about to knock). First 3 screens must re-hook *and* advance.
- **Chapter ending convention:** *Vertical cliff* — last screen is a reaction panel, a revealed object (a text notification, an unlocked door), or a zoom-to-face. Ending on dialogue is weak; ending on an image is strong.
- **Scene-to-scene transitions:** Scroll-driven whitespace acts as transition. Also: color-shift transitions (the whole color palette changes between scenes), "long fall" panels (a character falling or walking downward across a tall vertical frame to suggest time/distance).
- **Per-volume arc shape:** Webtoons do not publish in volumes natively; arcs are organized in "seasons" of 30–60 episodes, each ending on a major romantic beat. Season 1 typically ends at first confession or first major conflict.

## 4. Dialogue + narration
- **Register:** Contemporary, chat-native, short. Emojis-via-face-panel replace text emoji. Text-message panels (phone UI) are a core device.
- **Narration tolerance:** Low-to-moderate. Interior monologue appears as floating colored text rather than bordered captions.
- **Dialogue-to-narration ratio:** ~80:20.
- **Interior monologue:** Floating italic colored text on whitespace, used for heroine's reactions between dialogue beats. Must be short — 1–2 screen-sized lines.
- **Tell-don't-show tolerance:** Moderate — the heroine states her feeling frequently (modern reader expects interior access), but the love interest's interior is rationed to specific POV-gift episodes.

## 5. Character + arc conventions
- **Archetype grammar:** The self-conscious heroine with a *visible* vulnerability (makeup, body, class, power), the dual love interests (one warm/one cold — the "two-boy" engine is near-universal), the antagonist female peer, the supportive second-tier friend. *True Beauty* is the canonical template.
- **Emotional arc per volume (season):** Meet → misunderstand → forced proximity (school project, shared housing, workplace pairing) → emotional vulnerability leak → confession-adjacent moment → interruption → season cliff.
- **Cast density:** Small ensemble (5–9 named), with clear color-coding for instant mobile ID.

## 6. Failure modes
1. Print-style panel grids — kills vertical rhythm instantly.
2. Dialogue panels with more than 2 speech bubbles per screen-view — readers scroll past them.
3. Text-heavy narration captions — reads as "not a webtoon."
4. Color-palette drift — inconsistent emotional color-coding loses the reader's subconscious map.
5. Episodes without a hook ending — the subscriber churn is immediate and measurable.
6. Slow episodes with no micro-payoff (a touch, a text, a look) — the weekly contract demands one per episode.
7. Both love interests interior-narrated equally — the heroine's POV must dominate; the LI's interior is a *gift* episode.
8. Over-long megapanels without a rewarding beat at the bottom.
9. Ignoring phone/text UI as a storytelling tool.
10. Crossing into explicit content on a SFW platform without platform awareness (Lezhin vs Webtoon audience norms differ).

## 7. Series planning implications (48-"volume" pre-plan)
Webtoons are episodic-not-voluminous; map "volume" to a **season of ~25 episodes**. 48 volumes = ~1,200 episodes = ~23 years of weekly release (uncommon but not unprecedented — *Tower of God* is close). Realistic shape:
- **Season structure:** 48 seasons × 25 episodes = 1,200 episodes.
- **Romance arc pacing:** First confession at season 2–3 end (~vol 3). First kiss season 4 end. First real relationship crisis season 6. Breakup + reunion season 9–10. Engagement season 14. Post-marriage slice-of-life seasons 15–24. Then: next-generation time-skip for seasons 25–48 (children / workplace junior / new-romance spinoff with original couple as mentors).
- Each season must end on a confession-adjacent or crisis beat and open with 3-episode bounce-back.

## 8. Panel-level scaffolding for deterministic generation
Per-panel fields (8):
1. `canvas_slot` — which vertical screen-view this occupies (integer)
2. `panel_type` — {face_reaction, full_body, environment, text_ui, floating_thought, megapanel}
3. `framing` — CU / MCU / MS / environment
4. `dialogue` — ≤12 words; panels with >2 bubbles are blocked
5. `floating_thought` — interior, 1–2 lines, belongs to heroine unless `LI_pov_episode=true`
6. `color_register` — {warm, cool, high-sat-romantic, muted-sad, harsh-conflict, phone-UI} — emotional palette key
7. `scroll_beat` — {setup, micro-payoff, breath, hook-forward} — distribute so each episode has ≥3 micro-payoffs and ends on hook-forward
8. `phone_ui_flag` — boolean; true = render as iMessage/KakaoTalk-style panel

## 9. Three canonical chapter-opening examples

**A.**
The message had been sitting in her drafts for eleven minutes. [*see you tomorrow*] — no punctuation, no emoji, no read-receipt risk. Jihye stared at her phone. Jihye stared at her ceiling. Jihye stared at her phone. She typed a period at the end. She deleted the period. She added a heart, panicked, deleted the heart, added an exclamation mark, deleted the exclamation mark, and ultimately sent [*see you tomorrow*] at 1:47 a.m., then immediately locked her phone, turned it face-down, and shoved it under a pillow as if the pillow could retract a text message. The phone buzzed. She did not move. It buzzed again.

**B.**
Persephone had never seen snow until the morning it fell inside the apartment. She sat up in Hades's too-large bed, the sheets cool against her shoulders, and watched, for a full half-minute, small white flakes drifting down through the living-room doorway. She blinked. Snow. Indoors. She got out of bed slowly, pulled on the shirt that was not hers, and followed the flakes to the kitchen, where Hades stood in front of the open freezer holding a bag of ice, looking at her, looking at the ice, looking at her again. "I," he said. "I don't know how to make coffee."

**C.**
Jugyeong had been awake since 4 a.m. perfecting an eyeliner wing and she had just, at 7:52, ruined it. Not a small ruin. A *full tear of panic* ruin — the line dragged down to her cheekbone, mascara compounding the damage, the left eye now visibly crying and the right eye fine. School started in eight minutes. She stared at her reflection. Her reflection stared back, wet and dignified. From outside the bathroom door her mother shouted something she did not register. She picked up a cotton pad. She began again.

## 10. References
- Rachel Smythe, *Lore Olympus* Webtoon creator blog + interviews, *Polygon* 2020, 2022.
- Yaongyi interview on *True Beauty*, *Soompi* 2019.
- LINE Webtoon "Canvas to Originals" creator guide (public documentation).
- Park Joo-ha, "The Rise of the Vertical Scroll: Korean Webtoons and the Remediation of Comics," *Journal of Graphic Novels and Comics*, 2019.
- Dal Yong Jin, *Smartland Korea* (Michigan UP, 2017) — Webtoon industry chapter.
