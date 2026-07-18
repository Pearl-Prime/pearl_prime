# Full Funnel Plan — Phoenix Omega

**Authority:** Pearl_Marketing + Pearl_PM
**Status:** Active — canonical funnel reference
**Last updated:** 2026-04-10
**Subsystem:** brand_admin, core_pipeline, recommendations
**Project:** proj_state_convergence_20260328

---

## Funnel Architecture

```
SOCIAL (free)
  TikTok / Instagram Reels / YouTube Shorts / Facebook / Twitter-X / Pinterest
  Book-derived clips, quote cards, micro-practices (30–50 posts per book via 48 Social)
  CTA: "Free [Tool Name] → link in bio"
       ↓ 3–5% social CTR target
FREEBIE LANDING PAGE
  brand-admin-onboarding.pages.dev/free/{slug}/
  Email capture: name + email → instant access
  Tool/workbook/assessment rendered below the fold
       ↓ 25–40% email capture rate target
EMAIL PROOF LOOP (E1–E5 via GHL)
  E1 (0h):   Download + first exercise (somatic/practical, immediate)
  E2 (+24h): Second exercise, different mechanism
  E3 (+96h): Transformation story — proof the system works
  E4 (+144h): "$0.99 Book 1" offer — low-friction entry
  E5 (+312h): Books 2–7 in the series ($4.99 each) — upsell
       ↓ 8–15% E4 purchase rate target
$0.99 BOOK 1 (on platform)
  Series entry. Micro-book (20–30 min read). Proves the system.
  Platform: Google Play / Audible / Apple Books / Kobo
       ↓ 20–30% Book 1 → Book 2 conversion target
SERIES BOOKS 2–7 ($4.99 each)
  Each goes deeper into a different mechanism.
  Series landing: catalog.brand-admin-onboarding.pages.dev/{brand_id}
       ↓ ongoing LTV
VALUE LADDER CONTINUES
  Premium formats, bundles, companion workbooks, teacher courses
```

**Tooling per stage:**
| Stage | Content type | Platform | Tracking |
|-------|-------------|----------|----------|
| Social | Video clips, quote cards, carousels | 48 Social → Metricool | Platform analytics |
| Landing | Static HTML, email form | Cloudflare Pages | GA4 lead_submit event |
| Email | 5-email Proof Loop sequence | GHL automation | GHL open/click |
| Book 1 | Audiobook / ebook | Google Play / Audible / etc. | Platform dashboard |
| Series | Same platforms | Same | GHL buyer tag → upsell |

**Key principle:** Social IS the free tier. Platforms don't need a $0 book.
The freebie landing page is the conversion point, not the platform store.

---

## Per-Topic Funnel Map

### 1. Anxiety

**Consumer language:** "my mind won't shut up" / "chest tight for no reason" / "can't stop spiraling at 3am"
**Invisible script:** "I'm managing my anxiety well enough that no one can see it, but 'well enough' is a full-time job."
**Bridge:** "Your body's alarm system is working overtime — here's why."

```
SOCIAL CONTENT:
  Hook clips: "You did everything right. Your chest hasn't gotten the memo."
  Formats: 15–30s TikTok/Reels, quote cards, 5-slide carousels
  CTA: "Free Nervous System Reset Timer → link in bio"
  Platforms: TikTok (Gen Z), Instagram (millennials), YouTube Shorts (all)
  Hashtags: #nervoussystem #anxietyrelief #breathwork #highfunctioninganxiety

FREEBIE:
  Type: Interactive HTML tool (TYPE A — breath timer)
  Name: "90-Second Nervous System Reset"
  Slug: anxiety-nervous-system-reset
  What it does: Guided 4-7-8 breath timer with visual pacer + body check-in prompt
  Why it works: Immediate somatic experience — proves the mechanism before any ask
  Landing: /free/anxiety-nervous-system-reset/

EMAIL SEQUENCE:
  E1 (0h): "Your Reset Timer is ready — try this before you close this tab"
    Exercise: Place hand on chest, 3 breath cycles, notice the shift
  E2 (+24h): "What your alarm system is actually doing"
    Exercise: "Alarm noted. No action required." — say it out loud
  E3 (+96h): "She checked her phone 40 times before meetings"
    Story: Corporate manager who couldn't sit still; what changed
  E4 (+144h): "The full anxiety reset — $0.99"
    Offer: Calm Signal Series: The Alarm Is Lying
  E5 (+312h): "Books 2–7: go deeper into the pattern"
    Upsell: Calm Signal Series books 2–7 at $4.99 each

$0.99 BOOK 1:
  Title: Calm Signal Series: The Alarm Is Lying
  Subtitle: A Nervous System Guide to Anxiety Recovery
  Format: short_book_30 (30-min listen)
  Series: SER-279D9C44 (7 books)

METRICS:
  Social → freebie CTR: 3–5%
  Landing → email capture: 25–40%
  E4 → Book 1 purchase: 8–15%
  Book 1 → Book 2: 20–30%
```

---

### 2. Burnout

**Consumer language:** "running on fumes no matter how much I sleep" / "accomplished everything and still feel empty"
**Invisible script:** "I burned out quietly, so quietly that even I didn't notice until I did."
**Bridge:** "Burnout isn't laziness — it's your system hitting the limit."

```
SOCIAL CONTENT:
  Hook clips: "Burnout isn't just tired. It's soul-tired."
  Formats: TikTok text-on-screen, Instagram carousels, YouTube Shorts
  CTA: "Free Energy Audit → find where it's leaking → link in bio"
  Platforms: LinkedIn (corporate), Instagram (millennials), TikTok (gen Z)
  Hashtags: #burnout #burnoutrecovery #hustle #worktok #nervousystemreset

FREEBIE:
  Type: Downloadable workbook (TYPE B — PDF-ready HTML)
  Name: "The 5-Minute Energy Audit"
  Slug: burnout-energy-audit
  What it does: 10 reflection prompts mapping where energy is going vs. coming in
  Why it works: Pattern reveal — reader sees the drain before any prescription
  Landing: /free/burnout-energy-audit/

EMAIL SEQUENCE:
  E1 (0h): "Your Energy Audit is ready — 5 minutes, pencil optional"
    Exercise: One prompt: "What did I do yesterday that I resented doing?"
  E2 (+24h): "The exhaustion that sleep can't fix"
    Exercise: Body location scan — where do you carry the job?
  E3 (+96h): "He gave everything to a company that let him go"
    Story: Tech manager who rebuilt differently
  E4 (+144h): "The full burnout reset — $0.99"
    Offer: The Recovery Road Series: The Collapse You Earned
  E5 (+312h): "Books 2–7: rebuild on your own terms"
    Upsell: Recovery Road Series books 2–7

$0.99 BOOK 1:
  Title: The Recovery Road Series: The Collapse You Earned
  Subtitle: Burnout Recovery for People Who Can't Stop
  Format: short_book_30
  Series: SER-61A56EC7 (7 books)

METRICS: (same targets as anxiety)
```

---

### 3. Self-Worth

**Consumer language:** "I don't feel like I deserve good things" / "my worth is tied to what I produce"
**Invisible script:** "My worth is tied to my output, which is why I can't rest without feeling guilty."
**Bridge:** "Your worth isn't earned — it's inherent and unchanging."

```
SOCIAL CONTENT:
  Hook clips: "You're enough exactly as you are right now. Your brain disagrees. Let's fix that."
  Formats: Instagram quote cards, TikTok text posts, Pinterest
  CTA: "Free self-worth inventory → 3 minutes → link in bio"
  Platforms: Instagram (millennial women), TikTok (gen Z), Pinterest

FREEBIE:
  Type: Downloadable workbook (TYPE B)
  Name: "The Worth Inventory"
  Slug: self-worth-inventory
  What it does: Evidence-based exercise listing real proof of inherent worth — not achievements
  Why it works: Interrupts the conditional-worth loop with concrete counter-evidence
  Landing: /free/self-worth-inventory/

EMAIL SEQUENCE:
  E1 (0h): "Your Worth Inventory is ready — do this one before the day starts"
    Exercise: List 3 things about yourself that have nothing to do with output
  E2 (+24h): "The comparison trap and how to step out"
    Exercise: Catch one comparison thought today; name it; let it pass
  E3 (+96h): "She achieved everything and still felt like nothing"
    Story: Millennial professional who disconnected worth from output
  E4 (+144h): "The full self-worth reset — $0.99"
    Offer: The Enough Series: Worthy Without Proof
  E5 (+312h): "Books 2–7: go deeper"
    Upsell: The Enough Series 2–7

$0.99 BOOK 1:
  Title: The Enough Series: Worthy Without Proof
  Subtitle: How to Build Unshakable Self-Worth and Confidence
  Format: short_book_30
  Series: SER-EEC7097A (7 books)
```

---

### 4. Imposter Syndrome

**Consumer language:** "I don't deserve to be here — everyone will figure me out" / "my success doesn't feel real"
**Invisible script:** "I know I got here because I worked harder than everyone else, but I still feel like I'm about to be exposed."
**Bridge:** "Your doubt is usually louder than your evidence."

```
SOCIAL CONTENT:
  Hook clips: "The higher you climb, the louder the voice that says you don't belong."
  CTA: "Free evidence log — proves the voice wrong → link in bio"
  Platforms: LinkedIn (professionals), Instagram, TikTok

FREEBIE:
  Type: Interactive checklist (TYPE D)
  Name: "The Evidence Log"
  Slug: imposter-evidence-log
  What it does: Guided inventory of real proof of competence the imposter voice ignores
  Why it works: Makes the evidence concrete and visible — hard to argue with a list
  Landing: /free/imposter-evidence-log/

EMAIL SEQUENCE:
  E1 (0h): "Your Evidence Log is ready — fill in 3 rows before anything else today"
    Exercise: Write down one thing you actually know how to do. No caveats.
  E2 (+24h): "Why the imposter voice gets louder when you're succeeding"
    Exercise: Notice when the voice fires today — write down what triggered it
  E3 (+96h): "She was promoted twice and still waited for them to 'figure it out'"
    Story: Tech finance professional who learned to trust her evidence
  E4 (+144h): "The full imposter reset — $0.99"
    Offer: Own Your Seat Collection: You're Not a Fraud
  E5 (+312h): "Books 2–7 in the series"
    Upsell: Own Your Seat Collection 2–7

$0.99 BOOK 1:
  Title: Own Your Seat Collection: You're Not a Fraud
  Subtitle: How to Stop Waiting to Be Exposed and Start Owning What You've Built
  Format: short_book_30
```

---

### 5. Boundaries

**Consumer language:** "why do I always say yes when I mean no" / "setting a boundary feels selfish and mean"
**Invisible script:** "Setting a boundary feels like admitting I'm not enough to handle everything."
**Bridge:** "No is a complete sentence and you don't owe an explanation."

```
SOCIAL CONTENT:
  Hook clips: "People pleasing is a full-time job nobody hired you for."
  CTA: "Free boundary scripts — actual words to use → link in bio"
  Platforms: TikTok, Instagram, Facebook

FREEBIE:
  Type: Guided protocol / script kit (TYPE D)
  Name: "The Boundary Script Kit"
  Slug: boundaries-script-kit
  What it does: 8 real-world scenarios with exact scripts for each — no blank page
  Why it works: Removes the "I don't know what to say" block; action over theory
  Landing: /free/boundaries-script-kit/

EMAIL SEQUENCE:
  E1 (0h): "Your Boundary Script Kit is ready — use one today"
    Exercise: Read the 'family pressure' script. Notice your body's reaction.
  E2 (+24h): "Why saying no makes your body panic"
    Exercise: Say 'I can't do that' in the mirror — notice what happens
  E3 (+96h): "She said yes to everything until she had nothing left"
    Story: Working parent who learned what yes was costing
  E4 (+144h): "The full boundaries system — $0.99"
    Offer: No with Grace Collection: The No That Saved Me
  E5 (+312h): "Books 2–7: deeper practices"
    Upsell: No with Grace Collection 2–7

$0.99 BOOK 1:
  Title: No with Grace Collection: The No That Saved Me
  Subtitle: How to Set Boundaries Without Losing the People You Love
  Format: short_book_30
```

---

### 6. Depression

**Consumer language:** "nothing sounds good anymore even things I love" / "that fog in my brain where thoughts should be"
**Invisible script:** "Depression doesn't look like I thought it would on me, so I thought it wasn't real."
**Bridge:** "That heaviness isn't weakness — it's real and it's manageable."

```
SOCIAL CONTENT:
  Hook clips: "Depression isn't sadness. It's static."
  CTA: "Free momentum kit — 3-minute daily practice → link in bio"
  Platforms: TikTok (gen Z), Instagram, YouTube Shorts
  Note: Avoid clinical language. No "depression treatment" framing.

FREEBIE:
  Type: Interactive checklist (TYPE D)
  Name: "The Momentum Kit"
  Slug: depression-momentum-kit
  What it does: 5 micro-actions organized by energy cost — starts at zero effort
  Why it works: Bypasses the "I can't do anything" loop with genuinely small steps
  Landing: /free/depression-momentum-kit/

EMAIL SEQUENCE:
  E1 (0h): "Your Momentum Kit is ready — pick the one thing that costs the least"
    Exercise: Put both feet on the floor. That counted.
  E2 (+24h): "Why willpower doesn't work when nothing tastes right"
    Exercise: One tiny thing — fill in what yours will be today
  E3 (+96h): "She went through the motions for a year before something shifted"
    Story: Millennial woman who found movement through a different door
  E4 (+144h): "The full system — $0.99"
    Offer: Light Ahead Collection: Still Breathing
  E5 (+312h): "Books 2–7 in the collection"
    Upsell: Light Ahead Collection 2–7

$0.99 BOOK 1:
  Title: Light Ahead Collection: Still Breathing
  Subtitle: Depression Recovery for People Running on Empty
  Format: short_book_30
```

---

### 7. Courage

**Consumer language:** "want to do it but terrified of what happens" / "scared and doing it anyway is apparently courage"
**Invisible script:** "I'm brave at work but terrified in my own life — I haven't figured out what bravery actually is."
**Bridge:** "Courage is fear plus action — not fear's absence."

```
SOCIAL CONTENT:
  Hook clips: "You don't have to feel ready. You have to go anyway."
  CTA: "Free decision map — make the scary choice → link in bio"
  Platforms: TikTok, Instagram, YouTube

FREEBIE:
  Type: Guided protocol (TYPE D)
  Name: "The Decision Map"
  Slug: courage-decision-map
  What it does: 6-step clarity protocol for the one thing you're avoiding
  Why it works: Makes the fear concrete and the path visible — reduces the fog
  Landing: /free/courage-decision-map/

EMAIL SEQUENCE:
  E1 (0h): "Your Decision Map is ready — pick the one thing you've been avoiding"
    Exercise: Name it. Write it. Notice where you feel it in your body.
  E2 (+24h): "The moment right before you commit — what's actually happening"
    Exercise: Describe what 'doing it scared' would look like tomorrow
  E3 (+96h): "She stayed at the edge for two years before she jumped"
    Story: Entrepreneur who finally made the call
  E4 (+144h): "The full courage system — $0.99"
    Offer: Fear to Fire Collection: Jump Scared
  E5 (+312h): "Books 2–7"
    Upsell: Fear to Fire Collection 2–7

$0.99 BOOK 1:
  Title: Fear to Fire Collection: Jump Scared
  Subtitle: How to Move When Fear Is the Only Thing Stopping You
  Format: short_book_30
```

---

### 8. Overthinking

**Consumer language:** "replaying conversations from 5 years ago at 2am" / "my brain won't stop analyzing what I said"
**Invisible script:** "I've made success by thinking three steps ahead, so now my brain won't stop and I'm exhausted."
**Bridge:** "Your brain got stuck in investigate mode."

```
SOCIAL CONTENT:
  Hook clips: "Your brain isn't broken. It got stuck in investigate mode."
  CTA: "Free thought sorter — 2 minutes → link in bio"
  Platforms: TikTok, Instagram, Twitter-X (threads)

FREEBIE:
  Type: Interactive assessment (TYPE C)
  Name: "The Thought Sorter"
  Slug: overthinking-thought-sorter
  What it does: 8-question tool that labels thought loops by type (solve / process / worry)
  Why it works: Naming the loop interrupts it — turns anxiety into information
  Landing: /free/overthinking-thought-sorter/

EMAIL SEQUENCE:
  E1 (0h): "Your Thought Sorter result is ready — here's what it means"
    Exercise: Pick one thought from right now. Label it: solve, process, or worry.
  E2 (+24h): "The loop that's looking for certainty you can't find"
    Exercise: Next time the loop starts, say: 'I notice I'm looking for certainty'
  E3 (+96h): "He analyzed the job offer for three weeks and nearly lost it"
    Story: Tech professional who broke the pattern
  E4 (+144h): "The full overthinking reset — $0.99"
    Offer: Loop Breaker Collection: Your Brain Is Not the Boss
  E5 (+312h): "Books 2–7"
    Upsell: Loop Breaker Collection 2–7

$0.99 BOOK 1:
  Title: Loop Breaker Collection: Your Brain Is Not the Boss
  Subtitle: How to Stop Thinking in Circles and Start Moving Forward
  Format: short_book_30
```

---

### 9. Compassion Fatigue

**Consumer language:** "I care about people but I have nothing left" / "being there for everyone means there's nothing for me"
**Invisible script:** "I've been the therapist in every room, and somewhere I stopped knowing how to ask for help."
**Bridge:** "Caring deeply doesn't mean emptying yourself."

```
SOCIAL CONTENT:
  Hook clips: "Empathy without limits becomes exhaustion."
  CTA: "Free capacity audit — see where yours went → link in bio"
  Platforms: Instagram, TikTok, LinkedIn (healthcare, social work)

FREEBIE:
  Type: Assessment (TYPE C)
  Name: "The Capacity Audit"
  Slug: compassion-fatigue-audit
  What it does: 10-question self-assessment scoring emotional capacity vs. demand
  Why it works: Makes the gap visible — permission to refill before giving more
  Landing: /free/compassion-fatigue-audit/

EMAIL SEQUENCE:
  E1 (0h): "Your Capacity Audit result — here's what your score means"
    Exercise: Name one thing you need that you haven't asked for
  E2 (+24h): "Your nervous system mirrors theirs — that's the cost"
    Exercise: 2-minute boundary: one hour where you don't help anyone
  E3 (+96h): "The nurse who forgot she was allowed to need things too"
    Story: Healthcare RN who reclaimed her own oxygen
  E4 (+144h): "The full reset — $0.99"
    Offer: Empty Well Collection: Caring Until There's Nothing Left
  E5 (+312h): "Books 2–7"
    Upsell: Empty Well Collection 2–7

$0.99 BOOK 1:
  Title: Empty Well Collection: Caring Until There's Nothing Left
  Subtitle: How to Give Without Running Dry
  Format: short_book_30
```

---

### 10. Social Anxiety

**Consumer language:** "rooms full of people make me want to disappear" / "small talk is absolute torture"
**Invisible script:** "The more successful I become, the more convinced I am that people are only tolerating me."
**Bridge:** "Social anxiety is your threat detector working overtime."

```
SOCIAL CONTENT:
  Hook clips: "You're not awkward. Your alarm system is just miscalibrated."
  CTA: "Free social energy toolkit → link in bio"
  Platforms: TikTok, Instagram (gen Z, millennials)

FREEBIE:
  Type: Guided protocol (TYPE D)
  Name: "The Social Energy Toolkit"
  Slug: social-anxiety-toolkit
  What it does: Pre-event protocol + 3 in-the-moment tools + post-event debrief
  Why it works: Concrete prep reduces the unknown; tools interrupt the spiral in real time
  Landing: /free/social-anxiety-toolkit/

EMAIL SEQUENCE:
  E1 (0h): "Your Social Energy Toolkit is ready — use the pre-event protocol next time"
    Exercise: Before one social thing this week: 3 deep breaths, one intention
  E2 (+24h): "What's actually happening when your face gets hot"
    Exercise: Name it: 'my alarm fired.' Walk through the toolkit step
  E3 (+96h): "She left every party early for two years until she understood why"
    Story: Gen Z professional who rewired the pattern
  E4 (+144h): "The full social anxiety reset — $0.99"
    Offer: The Brave Room Series: Brave Enough to Show Up
  E5 (+312h): "Books 2–7"
    Upsell: The Brave Room Series 2–7

$0.99 BOOK 1:
  Title: The Brave Room Series: Brave Enough to Show Up
  Subtitle: How to Walk Into Any Room Without the Dread
  Format: short_book_30
```

---

### 11. Sleep Anxiety

**Consumer language:** "can't sleep — mind racing about tomorrow" / "the second I close my eyes my brain explodes"
**Invisible script:** "I can't sleep because I'm thinking about not being able to sleep — that spiral is the most honest thing about me."
**Bridge:** "Your brain is trying to solve tomorrow at midnight."

```
SOCIAL CONTENT:
  Hook clips: "The anxiety about sleep is the thing keeping you awake."
  CTA: "Free wind-down protocol — 8 minutes → link in bio"
  Platforms: TikTok, Instagram (evening content), YouTube

FREEBIE:
  Type: Interactive timer/protocol (TYPE A)
  Name: "The 8-Minute Wind-Down"
  Slug: sleep-anxiety-wind-down
  What it does: Timed 3-phase wind-down: body release (3 min) → breath reset (3 min) → mind dump (2 min)
  Why it works: Gives the problem-solving brain a job (the mind dump) so it stops freelancing
  Landing: /free/sleep-anxiety-wind-down/

EMAIL SEQUENCE:
  E1 (0h): "Your Wind-Down Protocol — run it tonight before you try to sleep"
    Exercise: The mind dump: write every open loop before you close the laptop
  E2 (+24h): "Why bed became a stage for your worries"
    Exercise: Body release practice — progressive muscle release, 3 muscle groups
  E3 (+96h): "She dreaded 9pm for a year — here's what shifted"
    Story: Millennial professional who reclaimed nighttime
  E4 (+144h): "The full sleep anxiety system — $0.99"
    Offer: Quiet Night Collection: The Quiet Hour
  E5 (+312h): "Books 2–7"
    Upsell: Quiet Night Collection 2–7

$0.99 BOOK 1:
  Title: Quiet Night Collection: The Quiet Hour
  Subtitle: How to Reclaim Sleep When Your Mind Won't Let You Rest
  Format: short_book_30
```

---

### 12. Financial Anxiety

**Consumer language:** "constantly stressed about money even when I'm okay" / "one unexpected bill and I panic"
**Invisible script:** "I make good money and still live like I'm one mistake away from losing everything."
**Bridge:** "Financial anxiety tells you stories that aren't true."

```
SOCIAL CONTENT:
  Hook clips: "Your bank account is fine. Your nervous system didn't get the update."
  CTA: "Free money check-in — understand your pattern → link in bio"
  Platforms: TikTok, Instagram, LinkedIn

FREEBIE:
  Type: Assessment (TYPE C)
  Name: "The Money Check-In"
  Slug: financial-anxiety-check-in
  What it does: 10-question assessment mapping the emotional layer of money stress
  Why it works: Separates the financial reality from the anxiety story — huge relief
  Landing: /free/financial-anxiety-check-in/

EMAIL SEQUENCE:
  E1 (0h): "Your Money Check-In results — here's what the pattern is telling you"
    Exercise: Name the worst-case story your brain runs most often. Write it down.
  E2 (+24h): "That pit in your stomach about money — it's inherited, not inevitable"
    Exercise: Trace one money belief back to where you learned it
  E3 (+96h): "She earned six figures and checked her account 8 times a day"
    Story: Tech professional who separated safety from balance
  E4 (+144h): "The full financial anxiety reset — $0.99"
    Offer: Worth Beyond Balance Collection: The Money Knot
  E5 (+312h): "Books 2–7"
    Upsell: Worth Beyond Balance Collection 2–7

$0.99 BOOK 1:
  Title: Worth Beyond Balance Collection: The Money Knot
  Subtitle: Untangle the Anxiety Behind Your Money Worry
  Format: short_book_30
```

---

### 13. Financial Stress

**Consumer language:** "never enough no matter how much I make" / "money conversations make me want to vomit"
**Invisible script:** "I calculate my financial safety margin like other people count sheep."
**Bridge:** "Security isn't about the number — it's about knowing yourself."

```
SOCIAL CONTENT:
  Hook clips: "You're not bad with money. You're wired for scarcity."
  CTA: "Free financial stress audit — 5 questions → link in bio"
  Platforms: TikTok, Instagram, Facebook

FREEBIE:
  Type: Workbook (TYPE B)
  Name: "The Financial Stress Audit"
  Slug: financial-stress-audit
  What it does: 5-prompt reflection mapping stress triggers, inherited money beliefs, and one concrete shift
  Why it works: Moves from chaos to legibility — naming the pattern reduces its power
  Landing: /free/financial-stress-audit/

EMAIL SEQUENCE:
  E1 (0h): "Your Financial Stress Audit is ready — do prompts 1 and 2 right now"
    Exercise: What is the first money memory you have? What did you decide then?
  E2 (+24h): "Money stress has a voice in your head — we can turn it down"
    Exercise: Write the story your money stress tells. Then write one counter-fact.
  E3 (+96h): "He earned more and more and still felt broke — until he saw this"
    Story: Entrepreneur who traced stress to its source
  E4 (+144h): "The full system — $0.99"
    Offer: The Money Peace Series: Worth More Than Your Balance
  E5 (+312h): "Books 2–7"
    Upsell: The Money Peace Series 2–7

$0.99 BOOK 1:
  Title: The Money Peace Series: Worth More Than Your Balance
  Subtitle: How to Stop Letting Money Stress Run Your Life
  Format: short_book_30
```

---

### 14. Somatic Healing

**Consumer language:** "my body holds all my stress and I can feel it" / "trauma is literally in my shoulders and jaw"
**Invisible script:** "My body has been keeping score longer than I've been paying attention to it."
**Bridge:** "Your body is smarter than your thoughts about what you need."

```
SOCIAL CONTENT:
  Hook clips: "Your jaw. Your shoulders. The base of your skull. That's not stress — it's stored."
  CTA: "Free body scan — 4 minutes → link in bio"
  Platforms: Instagram, TikTok, YouTube

FREEBIE:
  Type: Interactive somatic tool (TYPE A)
  Name: "The 4-Minute Body Scan"
  Slug: somatic-body-scan
  What it does: Guided timed body scan with 4 check-in zones and release prompts
  Why it works: Immediate felt experience of body intelligence — proves the premise
  Landing: /free/somatic-body-scan/

EMAIL SEQUENCE:
  E1 (0h): "Your Body Scan is ready — do it standing up"
    Exercise: Feet on floor, scan from jaw to belly — note what you find
  E2 (+24h): "That tightness is information, not a problem"
    Exercise: Find one place of tension. Put your hand there. Breathe into it.
  E3 (+96h): "She'd been holding her breath for two years and didn't know it"
    Story: Healthcare professional who learned to read her body's signals
  E4 (+144h): "The full somatic system — $0.99"
    Offer: The Body Knows Series: Held by the Body
  E5 (+312h): "Books 2–7"
    Upsell: The Body Knows Series 2–7

$0.99 BOOK 1:
  Title: The Body Knows Series: Held by the Body
  Subtitle: A Somatic Guide to Releasing What You're Carrying
  Format: short_book_30
```

---

### 15. Grief

**Consumer language:** "they're gone and I don't know how to do this" / "I don't want to move on because it feels like forgetting"
**Invisible script:** "I don't have time to grieve properly so I grieve in my car on the way to meetings."
**Bridge:** "This depth of pain means they mattered deeply to you."

```
SOCIAL CONTENT:
  Hook clips: "Grief doesn't have stages. It has waves."
  CTA: "Free letter template — say what's left unsaid → link in bio"
  Platforms: Instagram, Facebook, Pinterest (older demographics)

FREEBIE:
  Type: Guided expression template (TYPE D)
  Name: "The Letter You Didn't Get to Send"
  Slug: grief-letter-template
  What it does: Structured prompt sequence for an unsent letter — not advice, just space
  Why it works: Expression without obligation; the weight shifts when it's on paper
  Landing: /free/grief-letter-template/

EMAIL SEQUENCE:
  E1 (0h): "Your letter template is ready — there's no right way to do this"
    Exercise: Write the first sentence only. That's enough for today.
  E2 (+24h): "Your guilt about laughing is proof you're still human"
    Exercise: Write one thing they would have laughed at this week
  E3 (+96h): "She carried it alone until she found the words"
    Story: Person who found their way through expression, not advice
  E4 (+144h): "The full grief companion — $0.99"
    Offer: Still Standing Series: The Shape of Missing
  E5 (+312h): "Books 2–7 in the series"
    Upsell: Still Standing Series 2–7

$0.99 BOOK 1:
  Title: Still Standing Series: The Shape of Missing
  Subtitle: A Guide to Grief for the People Who Are Still Here
  Format: short_book_30
```

---

## Per-Persona Adaptations

The funnel structure is the same across personas. Messaging register shifts:

| Persona | Register | Key shift |
|---------|---------|-----------|
| **millennial_women_professionals** | Direct, competence-affirming | Lead with the hidden cost of managing it alone |
| **tech_finance_burnout** | Data-adjacent, efficiency framing | Frame tools as system optimization, not feelings work |
| **entrepreneurs** | Stakes-aware, autonomy-respecting | Frame as protecting the engine of the business |
| **working_parents** | Time-scarce, guilt-sensitive | Lead with brevity — "2 minutes", "tonight" |
| **gen_x_sandwich** | Pragmatic, no-guru | No spiritual language; practical output only |
| **corporate_managers** | Authority-safe | Position as leadership resilience, not vulnerability |
| **gen_z_professionals** | Casual, phone-first | Short form, instant value, no wall of text |
| **healthcare_rns** | Competence-affirming, shift-aware | "Between shifts"; validate expertise before anything else |
| **gen_alpha_students** | Relatable, low-stakes | No corporate framing; peer-level voice |
| **first_responders** | Strength-respecting, mission-aware | Position tools as operational readiness, not healing |
| **gen_z_student** | Authentic, low-pressure | No hustle framing; "you're allowed to not be okay" |

**Persona adaptation is applied at:**
- Social caption register (48 Social generates per persona)
- Freebie landing page headline
- Email E1–E3 subject lines
- E3 story protagonist selection

---

## Per-Market Adaptations (CJK6)

| Market | Primary channel | Email alternative | Freebie format note |
|--------|----------------|------------------|-------------------|
| **ja_JP** | LINE (not email) | LINE push messages | QR code on freebie page; indirect CTA; keigo register |
| **ko_KR** | KakaoTalk | KakaoTalk + email | 힐링(healing) framing; Naver blog SEO secondary |
| **zh_CN** | WeChat | WeChat service account | No Google/email funnel viable; 知识付费 platform framing |
| **zh_TW** | LINE + email hybrid | Both | Traditional Chinese; pragmatic-tech tone |
| **zh_HK** | Instagram + email | Email | Cantonese-adjacent; bilingual acceptable |
| **zh_SG** | Instagram + email | Email | English-first; Chinese secondary |
| **de_DE** | Email-primary | Email | Privacy-conscious; explicit opt-in language required |
| **fr_FR** | Instagram + email | Email | Cultural warmth; less direct than EN |
| **es_ES / es_US** | TikTok + Instagram | Email | High TikTok engagement; community framing |
| **it_IT** | Instagram + email | Email | Visual-first; warmth in copy |
| **hu_HU** | Facebook + email | Email | Facebook dominant; community groups effective |

**CJK special handling:**
- zh_CN: WeChat mini-programs replace landing pages; freebie delivered in-app
- ja_JP / zh_TW: LINE Official Account sends E1–E5 equivalent as LINE messages
- ko_KR: KakaoTalk channel messages replace or supplement email
- All CJK: Freebie slug URLs remain the same; landing pages display in locale language

---

## Metrics & Measurement

| Stage | Metric | Tool | Target |
|-------|--------|------|--------|
| Social → landing | CTR on bio link | Metricool / platform analytics | 3–5% |
| Landing → email | Form completion rate | GA4 `lead_submit` event | 25–40% |
| E1 open rate | Email opened | GHL campaigns | >50% (immediate send) |
| E2 click rate | Exercise link clicked | GHL | >15% |
| E3 open rate | Story email opened | GHL | >35% |
| E4 purchase | Book 1 bought | Platform dashboard + GHL tag | 8–15% of E4 sends |
| Book 1 → Book 2 | Second purchase | Platform + GHL upsell tag | 20–30% |
| List growth | New contacts/week | GHL contacts | 50+/week growing |
| Email list size | Active subscribers | GHL | 500 by month 3, 2,000 by month 6 |

**Optimization triggers:**
- CTR < 2%: Rewrite social CTA — more specific benefit, less generic
- Capture < 20%: Rewrite landing headline — match consumer language more exactly
- E4 < 5%: Add "soft E3.5" email with book excerpt before hard offer
- Book 1 → 2 < 15%: Add in-book CTA to Book 2 at chapter 10 of Book 1

---

## Config Wiring Reference

| Component | Config file | Purpose |
|-----------|------------|---------|
| Topic → freebie → book | `config/funnel/freebie_to_book_map.yaml` | Canonical lookup |
| Email sequences | `config/funnel/email_templates/{topic}_nurture_5.yaml` | Per-topic copy |
| Freebie landing pages | `brand-wizard-app/public/free/{slug}/index.html` | Static HTML pages |
| 48 Social CTAs | `config/funnel/freebie_to_book_map.yaml` → `social_cta` block | Per-topic CTA text |
| GHL automation trigger | GHL sub-account → workflow → freebie tag | Email sequence start |
| GA4 events | `lead_submit`, `second_tool_click`, `book_intent` | Conversion tracking |

---

*Document authority: Pearl_Marketing + Pearl_PM. Updated 2026-04-10.*
*Governed by: docs/FREEBIE_MARKETING_PLAN.md, docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md*
