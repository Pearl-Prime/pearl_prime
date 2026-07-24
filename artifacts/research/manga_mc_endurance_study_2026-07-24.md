# Manga MC Endurance Study — Enduring Main Characters Per Canonical Genre Family

**Date:** 2026-07-24
**Author:** Pearl_Research (manga process uplift Lane 04)
**Mission:** For each canonical genre family (the 25 ids in
`config/manga/canonical_genre_list.yaml`, matching
`config/manga/story_excellence_gates.yaml::genre_core_evidence`), name the genre's most
enduring/beloved main characters (≥3 exemplars from commercially proven series) and extract WHY:
trait architecture, endurance mechanics (what carries 100+ episodes), reader-bond devices,
documented anti-patterns, and a wellness-embed note.

**Machine-usable distillation:** `config/manga/mc_endurance_checklists.yaml` (per-family
`must_have[]` / `should_have[]` / `anti_patterns[]` / `endurance_mechanics[]`, each item anchored
back into this study). Lane 07 wires that file into the story excellence gate.

**Builds on (edit-in-place lineage, no parallel docs):**
- `docs/research/manga_craft/main_character_interaction_grammar_by_genre.md` (interaction layer)
- Craft bibles §5 (protagonist sections) under `docs/research/manga_craft/`
- `artifacts/research/popular_genre_ranking_2026-05-02.md` + 2026 refresh addendum
- `artifacts/research/marketing_grounded_per_genre_allocation_2026-05-13.md`
- `docs/research/manga_craft/teacher_apparatus_per_genre.md` + `config/manga/manga_mode_vessels.yaml`

## Method + confidence key

Evidence classes used per claim:

- **[W]** — web-verified this lane (2026-07-24 WebSearch/WebFetch; URL cited in §Sources).
- **[R]** — repo-pinned prior research (SHA'd docs listed above; citation named inline).
- **[K]** — industry-standard fact from serialized-publishing record (circulation figures,
  volume counts, run lengths as publicly reported by publishers/Oricon and mirrored on
  Wikipedia). Stable, widely-replicated facts; not re-fetched per item this lane.
- **[C]** — craft inference from the exemplar set (the WHY extraction). Falsifiable against the
  named exemplars; the confidence rating on each family reflects how contested the inference is.

Confidence ratings per family: **high** = ≥3 exemplars with [W]/[R]/[K] commercial proof AND the
craft extraction is consistent across all exemplars; **medium** = commercial proof solid but the
craft extraction generalizes from fewer clean cases (or the genre's market data is opaque, e.g.
CN cultivation).

Failure-cadence norms (reader-bond device 3) are stated as genre norms observed across the
exemplar set [C], not per-series statistics.

**Scope guard:** this study feeds MC *authoring and gating*. It does not change genre
allocations (`docs/GENRE_PORTFOLIO_PLAN.md` is operator-tier; see the market refresh addendum
verdicts in the two market docs).

---

## battle — Battle (action_battle bible)

**Exemplars (commercially proven):**

| MC | Series | Endurance proof |
|---|---|---|
| Monkey D. Luffy | One Piece | 27+ years serialized, 500M+ circulation; Oricon series #1 2025, #2 2026-H1 (1.60M) [W][R] |
| Son Goku | Dragon Ball / Super | 42 vols + ongoing Super; ~260M franchise circulation; template for the modern battle MC [K] |
| Yuji Itadori | Jujutsu Kaisen | 150M cumulative by 2026 [W]; carried Oricon #1 2024, #2 2025, #3 2026-H1 with sequel `Modulo` launching top-10 [W][R] |
| Tanjiro Kamado | Demon Slayer | ~150M circulation in ~5 serialized years — fastest climb in the genre's modern era [K] |
| Chihiro Rokuhira | Kagurabachi | 4M+ circulation by 2026 — the current new-generation launch proof [W] |

**1. Trait architecture.** Core want: a concrete external goal (become Pirate King / protect
people / avenge the father). Core need (hidden): belonging and grief-processing — Luffy needs a
crew more than a title; Tanjiro's want (cure Nezuko) is a grief-management structure. The genre
norm is **high moral clarity in the MC with ambiguity pushed to the antagonist** (bible §5:
villain embodies what the MC rejects in himself). Competence/vulnerability mix: visibly
inadequate at series start, but with one **non-negotiable moral competence** already maxed
(Luffy's loyalty, Tanjiro's kindness, Itadori's "proper death" ethic) — the body grows, the
values never do. Register: earnest-comic default with tonal permission to go fully serious in
arc climaxes; Kagurabachi's quiet, grief-forward Chihiro shows the register widening toward
seinen without losing the shonen contract [W].

**2. Endurance mechanics.** (a) **Renewable goal ladder:** the stated goal is unreachable by
design (Pirate King, strongest), so each arc mints a reachable sub-goal; the series never
exhausts its premise. (b) **Relationship engine:** crew/team accretion — every arc adds a bonded
character whose own wound can host a future arc (One Piece's crew-member backstory rotation is
the canonical form). (c) **Escalating capability ladder with visible cost:** power-ups are
paid for on the body (bible §5 "suffering made visible, recovery made legible"); JJK's
binding-vow economy is the modern cost-accounting form. (d) **Serial identity with episodic
texture:** long arcs, but each volume delivers at least one complete fight beat.

**3. Reader-bond devices.** Interiority is *low* by genre norm — the battle MC thinks in short
resolves, not essays; interiority is outsourced to witnesses (rival/team react-shots carry the
meaning). Catchphrase/visual-token anchoring is mandatory and heavily merchandised: straw hat,
checkered haori, "I'm gonna be King of the Pirates." Failure cadence: the MC **loses the first
meaningful fight of nearly every arc** — the loss is the arc's engine; final-arc losses are
converted to costs (a limb, a teacher, a vow) rather than defeats.

**4. Anti-patterns (documented).** Power-creep without ceiling and talk-no-jutsu resolution
(action_battle bible §6 items 1, 5). The **late-Bleach pattern** is the genre's canonical
endurance failure: escalation drift + ensemble abandonment produced the documented reader
decline that ended the series' magazine run in 2016 [K]. Mentor-death-as-default and
"meet-lose-train-win" repeated without structural variation (bible §6) are the other two
documented drop drivers. New-launch anti-pattern [W]: even a hit like Kagurabachi takes an
indefinite hiatus (June 2026) rather than dilute quality — schedule integrity over volume.

**5. Wellness-embed note.** Vessel: `action_battle.teacher` — "the sensei of the settled
strike" (`manga_mode_vessels.yaml`); doctrine rides the training arc, which the genre already
treats as sacred time. Somatic content embeds as fight-craft (breathing, stance, unclenching);
courage/resilience content embeds as the loss-recovery loop. The genre contract is broken only
if doctrine arrives as speech instead of drill — teaching must be *practiced on the body*, per
`teacher_apparatus_per_genre.md` (action_battle row).

**Confidence: high.** All five exemplars carry [W]/[K] commercial proof; craft extraction
consistent across all five and with the action_battle bible §5.

---

## romance — Romance (shojo_romance bible + romance_josei_drama lane)

**Exemplars (commercially proven):**

| MC | Series | Endurance proof |
|---|---|---|
| Tohru Honda | Fruits Basket | 23 vols + spinoffs, ~30M circulation; defines the modern earnest-heroine template (bible §5) [K][R] |
| Kyoko Mogami | Skip Beat! | 49+ volumes over 20+ years — the longest-running active shojo-romance MC [K] |
| Maya Kitajima | Glass Mask | 49 vols, ~50M circulation across five decades — the historical endurance record for a shojo lead [K] |
| Sawako Kuronuma | Kimi ni Todoke | 30 vols; misread-outsider heroine, full courtship-to-adulthood arc [K] |
| Kaoruko Waguri / Rintaro Tsumugi | The Fragrant Flower Blooms with Dignity | 2.04M copies 2025, 10M+ worldwide by early 2026 — the current romance riser [W] |

**1. Trait architecture.** Core want: to be loved / chosen. Core need: **self-authorship** —
the modern romance MC's real arc is becoming able to love and be loved without dissolving
(bible §6 item 10: the ending must rhyme with self-authorship, not institution). Competence mix:
socially undervalued but with one quietly excellent domain competence (Tohru's caregiving,
Kyoko's craft obsession, Maya's acting genius) that the love interest is the *first to see
accurately*. Moral clarity: high for the lead; the genre puts ambiguity in rivals and in timing,
not in the MC's decency. Register: earnest with mandatory comedic chibi release valves every few
pages (bible §6 item 6).

**2. Endurance mechanics.** (a) **The delay engine with renewable rungs:** proximity is gained
in small irreversible increments (bible §5's ladder); each arc converts one relationship state
to the next (notice → speak → confess → date → crisis → repair), and long runs chain multiple
couples or life-stages rather than stretching one courtship (bible §7 — 6–8 arcs per 48 vols,
never one). (b) **Domain-competence B-plot:** Skip Beat! and Glass Mask prove the 40+ volume
romance is carried by a vocation ladder (acting roles) that renews independent of the
relationship — romance states are scarce, competence rungs are not. (c) **Rival rotation with
rehabilitation:** rivals get arcs, then join the ensemble (bible §6 item 3), converting threat
into cast.

**3. Reader-bond devices.** Interiority is *maximal* — the heroine's caption voice is the
genre's primary surface (interaction grammar: proximity read through hands/eye-line + interior
caption). Visual tokens are relational, not personal: the umbrella, the seat gap, the almost-
touch. Failure cadence: one meaningful misunderstanding or setback **per volume**, repaired
with a small net proximity gain (bible §5: "a volume without a proximity gain fails") — the MC
"loses" constantly at small scale and almost never at arc scale.

**4. Anti-patterns (documented).** Confession too early drains the engine (bible §6 item 1);
love interest with permanently withheld interiority turns readers by mid-run (item 2); assault-
as-romance now documented as reader-unsafe for Gen-Z (item 4); heroine with no life outside the
romance (item 5 — Tohru cleans, Kyoko acts). Long-run-specific: letting the domain-competence
B-plot stall collapses the 40+ volume form into repetitive will-they-won't-they.

**5. Wellness-embed note.** Vessel: `romance_josei_drama.teacher` — "the beloved who rests"
(`manga_mode_vessels.yaml`): doctrine is *modeled by the partner's ease*, never lectured.
Social-anxiety and boundary content ride the genre's native machinery (the scan before
speaking, the withheld touch, the conversation she's been afraid to have — `GENRE_PORTFOLIO_PLAN.md`
romance row). Contract break: making the beloved a therapist-in-disguise who names the doctrine;
the genre requires it stay somatic and relational.

**Confidence: high.** Five exemplars spanning 1976–2026; craft extraction matches shojo_romance
bible §5–§7 point-for-point.

---

## healing — Healing / Iyashikei (iyashikei_minimalism bible)

**Exemplars (commercially proven):**

| MC | Series | Endurance proof |
|---|---|---|
| Frieren | Frieren: Beyond Journey's End | 35M+ copies by early 2026; Oricon series #3 2024, **#1 2026-H1** (1.62M) — the healing-register MC outselling all battle MCs [W][R] |
| Ginko | Mushishi | 10 vols, evergreen international backlist; the genre's wandering-witness template [K] |
| Alpha Hatsuseno | Yokohama Kaidashi Kikō | 14 vols; seasonal-cycle structure the iyashikei bible's 48-vol shape is built on [K][R] |
| Akari Mizunashi | Aria | 12+ vols + sequels; apprenticeship-as-calm template [K] |
| Maomao | The Apothecary Diaries | 45M cumulative by 2026 [W]; healing-mystery straddle proving the register's commercial ceiling rose |

**1. Trait architecture.** Core want: almost none — deliberately weak goal pressure (the bible's
"low-arousal atmospheric work"). Core need: **relation to time** — Frieren's entire series is a
need (understand what the years with Himmel meant) discovered after the want expired. The
healing MC is highly competent in a small domain (magic, mushi-lore, rowing, pharmacology) and
emotionally *under*-expressive; vulnerability is shown as belatedness — feeling arrives after
the moment. Moral clarity: high, gentle; conflict is weather, not villainy. Register: quiet,
observational, dry humor allowed.

**2. Endurance mechanics.** (a) **Episodic identity with a slow serial sediment:** each chapter
is a complete encounter (a mushi case, a customer, a village), while grief/time understanding
accumulates almost invisibly — Frieren's decades-long journey and Mushishi's case rotation both
renew indefinitely because the *world* supplies episodes, not the MC's goal. (b) **Witness
structure:** the MC is a professional visitor to other people's stories, so the cast refreshes
per chapter without churn-cost. (c) **Seasonal cycle:** volumes are seasons, not arcs
(iyashikei bible §7 — 12 × 4-vol cycles); return-with-difference replaces escalation.

**3. Reader-bond devices.** Interiority is sparse and *delayed* — the genre's signature beat is
the emotion named one scene (or one century) late; readers bond through recognition, not
identification-with-drive. Visual token: a ritual object (Frieren's grimoires, Ginko's
cigarette, the tea cup) recurring in calm compositions (interaction grammar: side-by-side,
shared attention target, no face-off). Failure cadence: near-zero conventional losses; instead
a **regret cadence** — roughly one missed-connection beat per episode that lands softly.

**4. Anti-patterns (documented).** "Nothing happens" stagnation — contemplative pacing without
per-chapter encounter completion (dark_fantasy bible §6 names the same trap; iyashikei fails
when the episode lacks even a small completed exchange). Naming the feelings kills the register
(index cross-lane note: iyashikei leaves feelings un-named; kodomomuke names them — confusing
the two flattens both). Forced escalation — importing arc stakes breaks the seasonal contract;
Apothecary Diaries shows the correct alternative (blend in a *mystery* engine, keep stakes
courtly-small).

**5. Wellness-embed note.** Vessel: `iyashikei.teacher` — "the tea-house hands"
(`manga_mode_vessels.yaml`): doctrine learned by watching hands, body settles before mind
agrees. This is Phoenix's anchor genre (`GENRE_PORTFOLIO_PLAN.md` — 34/37 brands); the somatic/
sleep/rest payload is genre-native and needs no disguise. Contract break: any explicit
therapeutic naming ("heal your trauma" is a banned-evidence phrase in
`story_excellence_gates.yaml`).

**Confidence: high.** Frieren's 2026-H1 Oricon #1 [W] plus three evergreen classics; extraction
matches the iyashikei bible and the 2026 refresh finding that the healing×fantasy blend is the
market's rising register.

---

## dark_fantasy — Dark Fantasy (dark_fantasy bible)

**Exemplars (commercially proven):**

| MC | Series | Endurance proof |
|---|---|---|
| Guts | Berserk | 42+ vols over 35+ years, ~70M circulation; series continued past the author's death by his studio — the genre's endurance monument [K][R] |
| Thorfinn | Vinland Saga | 28+ vols, 7M+ circulation; the genre's canonical want→need inversion (revenge → "I have no enemies") [K][R] |
| Denji | Chainsaw Man | 36M cumulative by 2026 [W]; Oricon top-5 2026-H1 while in Part 2 with no airing anime [W] |
| Eren Yeager | Attack on Titan | 34 vols, 140M circulation; completed — the genre's controlled-demolition endgame model [K] |
| Frieren | (straddle from healing) | grief-carrier register at Oricon #1 2026-H1 [W] |

**1. Trait architecture.** Core want: survival or revenge — deliberately *wrong* wants the
series exists to dismantle. Core need: meaning-making after loss (bible §5 "The Damaged
Carrier": the wound is the story engine, not the backstory). Competence: exceptional violence-
competence purchased at ruinous somatic and social cost; vulnerability is structural (Guts's
body is a ledger of losses). Moral clarity: **low by design** — the MC does harm, the antagonist
has coherent reasons (bible §5), and the reader is trusted to hold both. Register: grave, with
mandatory warmth pockets (bible §6 item 4: "Even Berserk has campfire scenes").

**2. Endurance mechanics.** (a) **Irreversibility ladder:** each stage costs something that
cannot be returned (bible §7 — one irreversible loss per 4-vol block); endurance comes from the
reader's investment in accumulated scar tissue, not from goal renewal. (b) **Want-to-need
conversion arc:** Thorfinn's revenge expires mid-series and the need (build a world without
war) takes over — the genre's proof that an MC can survive his own premise ending. (c)
**Burdened-dyad engine:** the MC carries someone (Casca, the found-family, Nezuko-pattern), so
relationship maintenance generates chapters even between battles (interaction grammar:
"burdened proximity"). (d) Denji-pattern: **appetite-scale management** — keeping wants small
(bread, touch, normalcy) lets escalation stay meaningful at any power level.

**3. Reader-bond devices.** Interiority: moderate, fragmentary — the genre voices the wound in
images and silence, not caption essays (bible §6 item 2 bans monologue-as-essay). Visual
tokens: the carried object (Dragonslayer sword, chainsaw cord, the brand/scar) doubles as the
wound made visible. Failure cadence: the MC loses **often and permanently** — roughly every
arc ends with a cost even in victory; the genre's bond is trust that the story will not
un-lose those losses (bible §6 item 8: no premature rescue).

**4. Anti-patterns (documented).** Grimdark-for-shock, trauma-as-spectacle, protagonist
immunity, nihilism-without-warmth (bible §6 items 1, 6, 7, 4 — the four documented drop
drivers). Straddle-specific: importing battle-genre power-fantasy resolution (a clean win that
erases cost) breaks the contract and is the most common cross-genre contamination.

**5. Wellness-embed note.** Vessel: `dark_fantasy.teacher` — "the Keeper / the living land"
(doctrine as observation, never advice — gold exemplar `the_forest_beneath_the_skin`). Grief
and trauma-recovery content is genre-native (`GENRE_PORTFOLIO_PLAN.md` names this the Mega-tier
grief shell; the plan's own golden example is the warrior at the grave whose shoulders finally
drop). Contract break: resolution before cost is paid — the wellness payload must be *carrying
weight differently*, never erasing it.

**Confidence: high.** Four [K]/[W]-proven exemplars + one straddle; extraction is the
dark_fantasy bible §5–§7 with 2026 currency added.

---

## sports — Sports (sports_competition bible)

**Exemplars (commercially proven):**

| MC | Series | Endurance proof |
|---|---|---|
| Yoichi Isagi | Blue Lock | 50M circulation by Sept 2025 [R]; Oricon #4 2025 AND #4 2026-H1 (1.27M) — top-5 two years running [W][R] |
| Ippo Makunouchi | Hajime no Ippo | 140+ volumes over 35+ years — the longest-running active sports MC [K][W] |
| Hanamichi Sakuragi | Slam Dunk | 31 vols, ~170M circulation — highest-circulation sports manga ever [K] |
| Shoyo Hinata | Haikyu!! | 45 vols, 60M+ circulation; completed with full career arc [K] |
| Tsubasa Ozora | Captain Tsubasa | 40+ years across sequel series, ~90M; the age-up-across-series endurance model [K] |

**1. Trait architecture.** Core want: win the match / go pro / be the best striker. Core need:
a *self* that survives scoring — Blue Lock literalizes this (ego as the explicit subject);
Sakuragi needs belonging he pretends is about a girl; Hinata needs to matter despite his body.
Competence mix: one freak asset (Hinata's jump, Sakuragi's athleticism, Isagi's spatial
awareness) inside general inadequacy — the genre's fairness contract requires the MC be
*visibly* worse than rivals at fundamentals early. Moral clarity: high; rivalry is love
language, not enmity (action_battle bible parallel; interaction grammar sports row). Register:
hot-blooded comic-earnest; seinen variants (Ippo late-run) allowed melancholy.

**2. Endurance mechanics.** (a) **The bracket is renewable forever:** tournament → nationals →
pro → world; the sport supplies an inexhaustible opponent ladder with built-in stakes — this is
why Ippo sustains 140+ volumes and why Captain Tsubasa can age its MC across decades. (b)
**Opponent-as-one-arc-protagonist:** each match borrows the rival's interiority (Haikyu's
losing-team POV chapters are the canonical form), refreshing emotional stakes without touching
the MC's core. (c) **Team ecology:** ensemble members' positions give every arc a second
storyline for free. (d) **Physical-ceiling realism as late-run fuel:** aging, injury, and
retirement questions (late Ippo) convert the capability ladder into mortality material.

**3. Reader-bond devices.** Interiority: mid-level, spiking inside play (time-dilated in-match
monologue is the genre's signature device — thought at the speed of a rally). Visual token:
jersey number, signature move name (genre-mandatory: readers chant move names). Failure
cadence: **the highest of any genre** — the MC loses roughly one major match per 2–3 arcs, and
the genre's most beloved beats are losses (Slam Dunk famously ends on a loss-adjacent
tournament exit; Blue Lock eliminates viewpoint characters constantly). Losing well IS the
reader bond.

**4. Anti-patterns (documented).** Undefeated-MC syndrome — a sports MC who never loses a
meaningful match kills the fairness contract [C, uniform across exemplar set]. Powerup drift —
importing battle-genre superpowers dissolves the sport's physics (the bible's realism
contract). Timeskip-to-pro without paying development panels — documented reader complaint
pattern in long-run sports serials [C]. Ensemble neglect (action_battle bible §6 item 7
applies doubly — a team sport with one character is a contradiction).

**5. Wellness-embed note.** Vessel: `sports_competition.teacher` — "the coach of the
unclenched" ("choke is bracing; flow is release"). Performance-anxiety, ADHD-hyperfocus, and
failure-recovery payloads are genre-native (`GENRE_PORTFOLIO_PLAN.md` sports row;
`focus_sprint` brand allocates 40% here). The 2026-05-13 allocation doc §2.2 documents sports
as Phoenix's largest relative underweight — this family is where MC-endurance craft meets the
portfolio's known gap. Contract break: doctrine delivered outside the body (a sports MC must
learn in drill, choke, and release — never in a counseling scene).

**Confidence: high.** Blue Lock's two-year Oricon top-5 [W][R] + three all-time exemplars;
failure-cadence claim is the genre's best-documented craft norm.

---

## workplace — Workplace (workplace_drama bible)

**Exemplars:** Kosaku Shima (*Kosaku Shima* series — 40+ years serialized, the MC promoted
through every corporate rank with a series rename per rank: section chief → president →
chairman; the genre's endurance record and its mechanism in one [K]). Retsuko (*Aggretsuko* —
multi-season Netflix franchise; the modern burnout register `GENRE_PORTFOLIO_PLAN.md` names
directly [R]). Narumi Momose & Hirotaka Nifuji (*Wotakoi: Love Is Hard for Otaku* — 10M+
circulation; workplace-romance hybrid [K]). Hataraki-man's Hiroko Matsukata (*Hataraki Man* —
josei workaholism classic [K]).

**1. Trait architecture.** Want: survive/succeed inside the institution. Need: a self that is
not the job title. Competence: genuinely good at the work (the genre requires professional
verisimilitude — bible §5); vulnerability leaks through body and after-hours scenes while the
office face holds. Moral clarity: medium — office politics require compromise the MC feels.
Register: deadpan-comic (Aggretsuko, Wotakoi) or procedural-earnest (Shima).

**2. Endurance mechanics.** (a) **The org chart is the ladder:** promotion, transfer, and
project rotation renew the premise indefinitely — Shima's rank-per-series structure is the
canonical form; each rank is a new social geometry with the same MC. (b) **Rotating colleague
ensemble:** offices legitimately churn cast (transfers, new hires) without betrayal of
continuity. (c) **Work-arc episodics:** each project/quarter/client is a complete arc slot.

**3. Reader-bond devices.** Interiority: the gap between spoken office language and interior
caption IS the genre's bond (Retsuko's death-metal interior is the literalized form). Visual
token: badge/desk/commute; the after-hours setting (izakaya, karaoke) as recurring honesty
zone. Failure cadence: frequent small institutional losses (passed over, overruled) —
roughly one per arc — with rare, highly-rationed real wins.

**4. Anti-patterns (documented).** Fantasy-competence drift (the MC winning every meeting kills
verisimilitude); villainizing the institution into cartoonery (the genre needs the org to stay
plausibly survivable); burnout content played only as gag with no cost ledger — the bible's
failure mode list flags losing the professional-detail honesty that anchors the register [R].

**5. Wellness-embed note.** Vessel: `workplace_drama.teacher` — "the custodian who's seen the
cycles" (doctrine in small acts: when to put the pen down). Burnout/imposter/financial-anxiety
payloads are genre-native (6 workplace brands live here per the index [R]). Contract break:
HR-seminar voice — doctrine must arrive from a peer-rank body, never a slide deck.

**Confidence: high** on mechanics (Shima's rank-ladder is unambiguous); medium on modern
JP-print market depth (the genre's current commercial weight is streaming/josei-digital more
than Oricon print [C]).

---

## mystery — Mystery (supernatural_mystery strategy route; psychological_thriller adjacency)

**Exemplars:** Conan Edogawa (*Detective Conan* — 100+ volumes over 30+ years, ~270M
circulation, top-3 best-selling manga ever; the episodic-engine endurance record [K][W]).
Maomao (*The Apothecary Diaries* — 45M by 2026 [W]; Oricon #4 2024 [R]; the cozy/court
mystery's current proof). Hajime Kindaichi (*Kindaichi Case Files* — 100M franchise across
35+ years [K]). Light Yagami & L (*Death Note* — 12 vols, 30M; the completion-model
counter-case: cat-and-mouse premises exhaust and must END [K]).

**1. Trait architecture.** Want: solve the case. Need: varies by subgenre — Conan needs his
stolen life back (frozen serial frame), Maomao needs to be allowed to be curious (autonomy).
Competence: the highest competence-to-vulnerability ratio of any genre — the mystery MC is
allowed to be near-infallible *at deduction* while socially or physically constrained (a
child's body; a servant's rank). Moral clarity: high for detectives; the genre stores its
darkness in cases, not the MC. Register: methodical with dry wit.

**2. Endurance mechanics.** (a) **The case is a perfect renewable unit:** world supplies
crimes indefinitely; MC identity is deliberately episodic (Conan barely changes across 100
volumes — *stasis is the feature*, per the interaction grammar's information-asymmetry frame).
(b) **The frozen serial spine:** one unresolvable serial question (the Black Organization;
Maomao's parentage/court position) is rationed a few panels per volume — enough to serialize
loyalty without spending the premise. (c) **Case-difficulty ladder** substitutes for power
escalation. Death Note proves the inverse: when the serial question IS the whole engine
(catch Kira), the series must complete in ~12 volumes — plan completion, not endurance.

**3. Reader-bond devices.** Interiority: withheld at deduction time (fair-play convention:
the reader sees clues, not conclusions), open at social time. Visual token: signature
deduction pose/prop (bow tie, glasses glint, Maomao's pout at poison). Failure cadence: the
MC almost never fails the case but **routinely fails the personal frame** (Conan can't
confess to Ran; Maomao's status reversals) — the personal loss cadence humanizes the
infallible detective.

**4. Anti-patterns (documented).** Breaking fair-play (clues the reader never saw) is the
genre's canonical trust-killer [C, uniform]. Letting the frozen serial question actually
advance too fast (the premise is spent) or too slow past reader patience (documented long-run
Conan criticism [K]). Making the detective's infallibility emotional as well as deductive —
an MC who is never socially wrong reads as smug.

**5. Wellness-embed note.** Nearest vessels: `supernatural_mystery.teacher` ("the medium who
reads the cold" — body signal before the ghost) and `psychological_thriller.teacher` ("the
detective who reads bodies"). Overthinking/anxiety payloads embed as deduction craft: the body
as first evidence. Contract break: solving a case via unearned intuition — doctrine must
strengthen, not replace, method.

**Confidence: high.** Conan alone anchors the episodic-endurance claim; Maomao provides the
2026-current cozy variant [W].

---

## horror — Horror (psychological_horror lane)

**Exemplars:** Kirie Goshima (*Uzumaki* — Junji Ito's most-sold work; US BookScan top-20 2024
[R]) — the witness-MC template. Tomie (*Tomie* — the **recurring entity as the endurance
anchor**: the "MC" of long-run horror is the dread-source, not the victim [K]). Yoshiki &
Hikaru (*The Summer Hikaru Died* — 4M and rising, Netflix adaptation signal [R][K]) — the
current intimate-dread proof. Momo Ayase & Okarun (*Dandadan* — Oricon #3 2025, top-10
2026-H1; horror-comedy straddle [W][R]).

**1. Trait architecture.** Horror inverts the endurance question: the *victim-witness* MC is
ordinary, permeable, and defined by susceptibility (Kirie sees the wrongness first and cannot
leave); the *entity* carries the icon function (Tomie's face IS the catchphrase). Modern
long-run horror (Dandadan, Hikaru) fuses both: an MC bonded to the wrong presence. Want:
restore normal. Need: acknowledge what normal was hiding. Moral clarity: high MC / cosmically
indifferent world. Register: dread punctured by domestic banality (the banality is load-
bearing).

**2. Endurance mechanics.** (a) **Anthology-with-anchor:** Ito's model — rotate victims,
keep the entity/town/spiral; the dread-source is the serial asset. (b) **Bonded-wrongness
serial:** Hikaru/Dandadan model — the MC's relationship to the entity deepens instead of
resolving, converting horror into (queer/romantic/comic) intimacy stakes that renew like a
romance ladder. (c) **Escalating containment failure:** each arc widens what the wrongness
touches (interaction grammar: spatial wrongness made social).

**3. Reader-bond devices.** Interiority: high-frequency somatic narration (held breath, skin,
freeze response — the genre reads the body constantly). Visual token: the entity's fixed
visual signature (spiral, smile, silhouette) repeated with variation. Failure cadence: the MC
**loses nearly every encounter** — survival, not victory, is the win condition; permanent
marks accumulate.

**4. Anti-patterns (documented).** Over-exposing the entity (full explanation or constant
visibility collapses dread — the genre's most-documented failure [C, uniform]). Gore
substituting for wrongness (trauma-as-spectacle; parallels dark_fantasy §4). Victim carousel
with no anchor (pure anthology without a recurring dread-source has no serial asset). Comedy
straddles that release ALL tension (Dandadan's craft is withholding the release on one thread
while venting on another [W]).

**5. Wellness-embed note.** Vessel: `psychological_horror.teacher` — "the survivor who turns
toward it" (the only way out is through). Anxiety-as-entity is the `GENRE_PORTFOLIO_PLAN.md`
anchor embed (the creature only she can see); intrusive-thought and shame payloads are genre-
native. Contract break: exposure-therapy language on the page — the turn-toward must stay
enacted, never named.

**Confidence: high** for mechanics; medium for the bonded-wrongness serial claim's long-run
ceiling (Hikaru/Dandadan are young series [C]).

---

## essay — Essay / Reflective (seinen_psychological bible route)

**Exemplars:** Punpun Onodera (*Goodnight Punpun* — 13 vols, ~3M; the repo's own named ceiling
case for unshelled psychological content [R][K]). Shoya Ishida (*A Silent Voice* — 7 vols,
completion model; redemption-essay structure [K]). Meiko Inoue (*Solanin* — 2 vols + sequel;
quarter-life essay register [K]). Nagata Kabi (*My Lesbian Experience with Loneliness* line —
the serialized-self: 6+ autobiographical volumes where the AUTHOR-persona is the enduring MC
[K]).

**1. Trait architecture.** Want: articulate the un-articulable (usually disguised as small
life goals). Need: self-forgiveness. Competence: verbal/observational precision; life
competence deliberately low. Moral clarity: low-medium — the essay MC is allowed to be wrong,
petty, and complicit (Punpun's spiral) in ways no other genre's MC is. Register: confessional,
symbol-substituted (Punpun's bird-form is the genre's canonical interiority device [R]).

**2. Endurance mechanics.** Essay is a **completion-first family**: individual works run
2–13 volumes and END (the bible's 48-vol shape is 4 × 12-vol *eras*, not one arc [R]).
Endurance lives at the *persona* level: Nagata Kabi's readership follows the serialized self
across books — sequel-by-life-event. For Phoenix: plan essay lanes as bounded works under a
persistent author-persona, not open serials.

**3. Reader-bond devices.** Interiority: total — caption-dense, diaristic (josei_adult_memoir
bible: caption-dense confessional [R]). Visual token: the avatar-substitution (bird Punpun,
Kabi's self-caricature) that licenses honesty. Failure cadence: constant micro-failure; the
bond is recognition ("I have thought this and never said it").

**4. Anti-patterns (documented).** Transformation-arc imposition — the bible states the form
*resists* transformation arcs; a tidy cure ending breaks trust [R]. Wallowing without craft
(misery must be composed). Persona inconsistency across sequels (the serialized self must
stay recognizably continuous). The 3M ceiling itself [R]: essay without a genre shell caps
commercially — allocate accordingly, don't fight it with volume.

**5. Wellness-embed note.** No dedicated vessel — essay is the one family where doctrine may
surface as *named reflection* without breaking contract (the essayist is allowed to conclude).
Nearest apparatus: memoir's artifact-pole (interaction grammar: phone, diary, ceiling, scar).
Anti-drift guard: WISDOM_ESSENCE-style rulings still apply — reflection, not sermon.

**Confidence: high** (the family's mechanics are well-documented in-repo; ceiling is
repo-pinned [R]).

---

## slice_of_life — Slice of Life

**Exemplars:** Yotsuba Koiwai (*Yotsuba&!* — 15+ vols over 20+ years with no aging; the
episodic no-continuity endurance monument [K]). Rin Shima & Nadeshiko (*Laid-Back Camp* —
17+ vols, 10M+; hobby-anchored SoL [K]). Sazae Fuyuhara → see family. Kotaro (*Kotaro Lives
Alone* — premise-tension SoL [K]). Fukumaru & Kanda (*A Man and His Cat* — 10+ vols; the
repo's own Anchor-tier comparable [R]).

**1. Trait architecture.** Want: today's small concrete thing (the campsite, the pancake).
Need: none pressing — the genre's radical move is an MC whose needs are already mostly met,
making micro-variation legible. Competence: enthusiastic amateur or quiet hobbyist.
Moral clarity: total. Register: warm, observational, gently comic.

**2. Endurance mechanics.** (a) **Frozen-time episodics:** Yotsuba never ages; the world
resets each chapter — endurance via infinite present. (b) **Hobby-rotation engine:** the
hobby supplies destinations/gear/seasons as renewable episode seeds (Laid-Back Camp's
campsite-per-arc). (c) **Routine-with-variation:** the interaction grammar's "routine pair +
small variation" is the chapter algorithm itself.

**3. Reader-bond devices.** Interiority: light; the camera does the noticing. Visual token:
the hobby object / the child's found-object of the week. Failure cadence: micro-mishaps only
(burnt dinner, missed bus) resolved within-chapter — the genre's promise is that nothing is
ever truly lost.

**4. Anti-patterns (documented).** Imported drama (a real threat breaks the safety contract).
Aging up an explicitly frozen cast (continuity where none was promised). Hobby-detail
inaccuracy (the hobby audience is expert). Cast bloat past the small-ensemble grammar [C,
uniform; matches iyashikei's stagnation inverse — SoL fails by adding, iyashikei by
subtracting].

**5. Wellness-embed note.** Nearest vessel: `iyashikei.teacher` (tea-house hands) — SoL and
healing share the somatic-ritual apparatus; SoL adds the hobby as legitimizing structure
(rest permission disguised as camping). Contract break: mindfulness vocabulary on the page.

**Confidence: high.**

---

## fantasy_adventure — Fantasy Adventure (incl. isekai alias)

**Exemplars:** Frieren (straddle-lead — see healing; the family's current #1 commercial proof
[W]). Rimuru Tempest (*That Time I Got Reincarnated as a Slime* — 40M+ franchise; the
community-builder isekai template [K]). Sung Jinwoo (*Solo Leveling* — vol 24 Oricon #1
March 2026, ~51k first week [R]; the system-ladder MC). Coco (*Witch Hat Atelier* — 5M+,
Eisner-winning; the apprenticeship-wonder template [K]). Naofumi (*Shield Hero* — 11M;
the betrayed-outsider variant [K]).

**1. Trait architecture.** Want: the quest/return/rank. Need: a home worth having (nearly
universal across the exemplar set — the adventure is secretly about belonging). Competence:
either system-granted (isekai: menu screens, cheat skill) or apprenticed (Coco); the genre
splits on whether competence is *given* or *earned*, and the 2025 isekai glut [R: 32 new
series, ANN] is documented fatigue with *given*. Moral clarity: high; ambiguity lives in the
world's rules. Register: wonder-forward.

**2. Endurance mechanics.** (a) **The map is the ladder:** new region = new arc; world-
building depth is the renewable resource (the genre's endurance titans are world-first).
(b) **System/rank ladder** (Solo Leveling): quantified progression gives every chapter a
legible delta — high-velocity but exhaustible; plan a ceiling. (c) **Party accretion**
mirrors battle's crew engine. (d) **Quest-expiry conversion:** Frieren's model — the quest
already ended; walking it again *in memory* renews the same map at emotional depth.

**3. Reader-bond devices.** Interiority: medium; wonder is carried visually (interaction
grammar: rule object, threshold, map, scale). Visual token: the class/artifact signature
(shield, staff, grimoire). Failure cadence: moderate — setbacks reroute the journey rather
than defeat the MC; isekai variants under-use failure (documented sameness driver [R]).

**4. Anti-patterns (documented).** Power-fantasy sameness — the 2025 isekai saturation is the
family's named market risk [R: popular_genre_ranking §pipeline]; an MC who cannot lose plus a
world that only admires him is the drop pattern. World-rule inconsistency (the genre's fair-
play equivalent). Party members as inventory. Quest-goal drift without conversion (contrast
Frieren's deliberate conversion).

**5. Wellness-embed note.** Vessel: `isekai.teacher` — "the guide who trusts old instincts"
(the body's old-world map is truest). Second-chance/self-worth payloads are the family's
anchor embeds (`GENRE_PORTFOLIO_PLAN.md` isekai row: "am I meant to be here?"). Contract
break: the new world explicitly diagnosing the MC.

**Confidence: high.**

---

## food — Food

**Exemplars:** Yamaoka Shiro (*Oishinbo* — 111 volumes, ~135M; the food-endurance record via
theme-per-chapter format [K]). Kazumi Araiwa (*Cooking Papa* — 170+ vols, ongoing 40+ years;
domestic-recipe episodic [K]). Goro Inogashira (*Kodoku no Gourmet* — 30+ years incl.
long-run TV franchise; the solitary-eating witness template [K]). Soma Yukihira (*Food Wars*
— 20M repo-cited [R]; tournament-food hybrid).

**1. Trait architecture.** Want: this dish/meal/customer served right. Need: connection —
food manga MCs are connectors whose cooking/eating repairs some small human gap per chapter
(interaction grammar: "food is relationship made edible"). Competence: deep craft knowledge
worn lightly (Goro is merely an appreciator — expertise optional, attention mandatory).
Moral clarity: total. Register: sensory-maximalist, warm or comic.

**2. Endurance mechanics.** (a) **The menu is infinite:** dish-per-chapter is the purest
renewable episodic in manga — Oishinbo ran 111 volumes on theme-of-the-week. (b) **The
customer/companion slot:** each chapter's guest brings the human stakes; cast refreshes
free. (c) Competitive variant (Food Wars) borrows sports bracket mechanics — higher heat,
faster exhaustion (completed at 36 vols).

**3. Reader-bond devices.** Interiority: reaction-interiority — the taste monologue is the
genre's signature aria. Visual token: the signature dish / the eating face. Failure
cadence: low; failed dishes are within-chapter setbacks. The bond is appetite plus
vicarious care.

**4. Anti-patterns (documented).** Recipe-accuracy failure (the audience cooks). Reaction
inflation (every dish a cosmic event — Food Wars' late-run documented fatigue [C]).
Forgetting the human gap (food with no one to feed). Ingredient-lecture drift (Oishinbo's
own late-volume tendency [K]).

**5. Wellness-embed note.** No dedicated vessel; nearest = `iyashikei.teacher` (the meal as
ritual). Somatic/nourishment payloads ride the genre natively (eating as self-regard;
`hormone_reset`/`bio_flow` brand adjacency). Contract break: nutrition-sermon voice.

**Confidence: high** on mechanics; medium on current-market weight (family is
JP-print-stable, small in Phoenix portfolio [R]).

---

## family — Family

**Exemplars:** Sazae (*Sazae-san* — 68 vols, ~86M, plus the longest-running animated
adaptation on earth; the family-endurance institution [K]). Nobita & Doraemon (*Doraemon* —
45 vols, 100M+ print + 300M franchise; gadget-per-chapter family episodic [K]). Anya /
Loid / Yor (*Spy×Family* — 41M repo-cited [R]; Oricon top-10 2024 [R]; the constructed-
family engine's current proof). Shinnosuke (*Crayon Shin-chan* — 50 vols, ~148M [K]).

**1. Trait architecture.** The family MC is usually a **dyad or triad**, not a person — the
household is the protagonist (interaction grammar: household task circle). Focal members:
the disruptive child (Anya, Shin-chan) or the anchoring parent (Sazae). Want: keep the
household running / keep the secret. Need: be known inside the role. Competence:
domestic-practical; deliberately unheroic. Moral clarity: high, mischief-tolerant.
Register: comic-warm with rationed sincerity spikes.

**2. Endurance mechanics.** (a) **Frozen-age episodic:** Sazae-san and Shin-chan never age;
domestic micro-events renew forever. (b) **The secret-keeping engine** (Spy×Family): each
member's hidden identity generates misunderstanding comedy per chapter while the *real*
serial (becoming an actual family) advances glacially — the modern form of the frozen
spine. (c) **Occasion rotation:** school events, holidays, relatives — the calendar is the
map.

**3. Reader-bond devices.** Interiority: the child's unfiltered read (Anya's telepathy is
the device literalized). Visual token: the household object (dinner table, gadget-of-the-
week). Failure cadence: domestic pratfall per chapter, zero permanent losses.

**4. Anti-patterns (documented).** Aging the frozen cast (see slice_of_life). Advancing the
secret-reveal too far (Spy×Family's engine depends on NOT resolving — same rationing rule
as mystery's frozen spine). Parent incompetence played past believability. Sincerity
starvation (all-gag family manga loses the warmth that differentiates the family frame [C]).

**5. Wellness-embed note.** No dedicated vessel; nearest = `romance_josei_drama.teacher`
("the beloved who rests" generalizes to the household member who models ease —
`resilient_parent` brand row [R]). Parenting-burnout/self-worth payloads ride domestic
task-sharing beats. Contract break: parenting-manual voice.

**Confidence: high.**

---

## procedural — Procedural

**Exemplars:** Duke Togo (*Golgo 13* — 201+ volumes, Guinness record for most volumes of a
single manga [W]; the absolute endurance record in the medium). Kankichi Ryotsu
(*Kochikame* — 200 volumes, 1976–2016, ~156M [W][K]). Black Jack (*Black Jack* — ~25 vols,
Tezuka's operation-per-chapter template; the medical procedural's foundation [K]). Kii
Kanna? — modern medical: *Radiation House* / *Unsung Cinderella* tier [K, weaker].

**1. Trait architecture.** The procedural MC is a **fixed instrument**: Golgo's defining
trait is that he does not change in 200+ volumes — no arc, no backstory resolution, total
competence. Character is replaced by *method*; the client/case of the week carries all
emotional variance. Want: complete the job. Need: none admitted (the withheld interior IS
the mystique). Moral clarity: professional code, not conventional morality (Golgo, Black
Jack's fees). Register: terse, exact.

**2. Endurance mechanics.** (a) **Pure case engine at maximum stasis:** the world brings
the problem; the MC's invariance is the product — readers buy the guarantee, like a genre
itself. This is the deepest episodic endurance in manga and the direct structural cousin
of Phoenix's teacher-mode: an unchanging competence that each guest's story bends around.
(b) **Client-of-the-week interiority transfer** (Black Jack: the patient's story is the
chapter). (c) Comedy variant (Ryotsu): the scheme-of-the-week with a reset button plus
**topicality refresh** — Kochikame endured 40 years by absorbing each era's fads [W].

**3. Reader-bond devices.** Interiority: near-zero for the MC (the genre's inversion:
readers bond with the *guarantee*, and with clients). Visual token: the instrument (M16,
scalpel, the uniform). Failure cadence: almost never fails the job; the rare exception
becomes legendary (Golgo's handful of imperfect jobs are fan-canon events [K]).

**4. Anti-patterns (documented).** Giving the fixed instrument an arc (backstory resolution
destroys the guarantee). Case sameness without client variance (the variance budget lives
entirely in the guest). Topicality neglect in comic procedurals (Kochikame's counter-
strategy is the documented fix [W]). Ethics drift without the code (Black Jack's fee code
is what makes his mercy legible).

**5. Wellness-embed note.** No dedicated vessel; the procedural IS a vessel-shaped genre —
`teacher_apparatus_per_genre.md`'s hard rule (teacher never named, doctrine earned through
method) matches the procedural contract exactly. Payloads ride the client-of-the-week's
wound; the MC's method models regulation without ever naming it. Contract break: the
instrument-MC self-disclosing.

**Confidence: high** (Guinness-anchored [W]).

---

## historical — Historical (historical_period bible)

**Exemplars:** Li Xin / Ei Sei (*Kingdom* — 120M cumulative by 2026 [W]; 70+ volumes
ongoing; Oricon #5 2025 [R]; the historical endurance king). Thorfinn (*Vinland Saga* —
28+ vols, 7M+ [R][K]). Miyamoto Musashi (*Vagabond* — 37 vols, ~82M; hiatus-frozen but
evergreen [K]). Amir (*A Bride's Story* — 14+ vols; the domestic-historical variant [K]).
Kenshin Himura (*Rurouni Kenshin* — 28 vols, 72M [K]).

**1. Trait architecture.** Want: rank/conquest/survival within the period's terms. Need:
an ethic the period does not supply (Thorfinn's "I have no enemies"; Kenshin's no-kill
vow) — the historical MC's need is usually *ahead of* his era, which is the genre's bridge
to modern readers. Competence: period-craft mastery (war, sword, homestead). Moral
clarity: medium — period-accurate values create productive friction. Register: grave,
materially dense (bible: period object + rank distance [R]).

**2. Endurance mechanics.** (a) **History is a pre-written ladder:** campaigns, eras, and
recorded events give Kingdom an inexhaustible arc supply with built-in stakes — the
reader's history knowledge is anticipation, not spoiler. (b) **Vow-arc spine:** the
era-ahead ethic is tested once per arc (Kenshin's vow; Thorfinn's pacifism) — a renewable
moral bracket. (c) **Generational handoff** (A Bride's Story's cast-of-households;
Vinland's act structure) renews cast within period.

**3. Reader-bond devices.** Interiority: restrained; period speech discipline pushes
feeling into material detail (the bible's period-object rule). Visual token:
period-accurate signature gear (reverse-blade sword, glaive, the loom). Failure cadence:
battle losses and political reversals are frequent and REAL (history doesn't protect
anyone) — the genre's stakes credibility depends on it.

**4. Anti-patterns (documented).** Modern casual spacing/speech (interaction grammar's
named avoid [R]). Period-detail error (the audience is expert — parallels food/sports
accuracy contracts). Vow made trivial (if the no-kill vow never costs, it's decor).
Great-man drift (losing the ensemble's period texture to one hero's plot armor —
Kingdom's craft is that named historical figures still die on schedule [C]).

**5. Wellness-embed note.** Vessel: `historical_period.teacher` — "the workshop hands that
refuse hurry" (M4-upgraded: material-demanded pause [R]). Legacy/grief-across-time
payloads are genre-native (`legacy_builder`, `stoic_edge` brands [R]). Contract break:
anachronistic therapy vocabulary.

**Confidence: high** (Kingdom 2026 figure [W]).

---

## comedy — Comedy (comedy_gag bible)

**Exemplars:** Kankichi Ryotsu (*Kochikame* — 200 vols over 40 years [W]; the comedy
endurance record). Gintoki Sakata (*Gintama* — 77 vols, ~55M; parody-engine endurance [K]).
Kusuo Saiki (*The Disastrous Life of Saiki K.* — 26 vols; the deadpan-overpowered template
[K]). Anya Forger (*Spy×Family* — the current comedy-face straddle [R]). Retsuko
(workplace straddle [R]).

**1. Trait architecture.** The comedy MC is a **stable eccentric**: one fixed comic engine
(greed + scheme, laziness + competence, omnipotence + desire for normalcy) that never
resolves. Want: petty and concrete (money, sleep, peace). Need: officially none — sneaking
sincerity in is the long-run craft (Gintama's rationed drama arcs). Moral clarity: elastic
within harmlessness. Register: high-tempo with a straight-man axis (interaction grammar:
straight person / chaos agent / witnesses [R]).

**2. Endurance mechanics.** (a) **Format rotation:** the gag engine stays fixed while
formats rotate (parody-of-the-week, scheme-of-the-week, guest-of-the-week) — Kochikame's
documented topicality absorption is the 40-year mechanism [W]. (b) **Ensemble reaction
economy:** a deep bench of straight-persons keeps the same joke fresh by rotating who
suffers it. (c) **Sincerity rationing:** rare earnest arcs (Gintama's serious arcs)
re-charge the comedy by proving stakes exist.

**3. Reader-bond devices.** Interiority: punchline-interiority (the MC's inner voice is
the joke's second beat — Saiki's deadpan narration). Visual token: fixed silhouette + one
absurd attribute (Ryotsu's eyebrows, Saiki's antennae). Failure cadence: the MC loses
EVERY scheme (comedy's engine is failure) but never pays permanent cost — the inverse of
dark_fantasy's ledger.

**4. Anti-patterns (documented).** Formula exhaustion without format rotation (bible §6
[R]; Kochikame's counter-example is the fix [W]). Sincerity flooding (too many serious
arcs and the contract flips). Punching down (modern reader-safety norm; parallels shojo's
assault-framing update [R]). Chaos agent with no straight-man axis (the grammar's named
requirement [R]).

**5. Wellness-embed note.** No dedicated vessel; comedy carries wellness as **status-flip
relief** — the `GENRE_PORTFOLIO_PLAN.md` workplace-comedy row (Aggretsuko register) shows
the embed: name the absurdity of the pressure, let laughter discharge it. Contract break:
the joke stopping for the lesson.

**Confidence: high.**

---

## cultivation — Cultivation / Progression Fantasy (cultivation_martial bible)

**Exemplars:** Tang San (*Soul Land* / Douluo Dalu — the CN progression flagship;
multi-platform franchise [K]). Han Li (*A Record of a Mortal's Journey to Immortality* —
the bible's named register anchor: the cautious mortal grinding through tiers [R][K]).
Xiao Yan (*Battle Through the Heavens* — the humiliation-comeback template [R][K]).
Sung Jinwoo (*Solo Leveling* — KR system-adjacent straddle; Oricon-verified 2026 print
success [R]).

**1. Trait architecture.** Want: ascend the power tiers. Need: keep the self that started
climbing (the genre's tragedy risk: ascension hollows). Competence: relentless,
methodical grind — talent is usually *average-plus-hidden-asset* (Han Li's caution IS the
asset). Moral clarity: pragmatic-medium; face/reputation stakes drive conflict alongside
raw power (bible: the key divergence from JP shonen [R]). Register: strategic, ledger-
like (resources, pills, techniques counted).

**2. Endurance mechanics.** (a) **The tier ladder is explicitly infinite:** realms nest
(mortal → immortal → …), giving the purest quantified endurance engine in comics — CN
web-serials run thousands of chapters on it. (b) **Sect/rival ecology:** each realm
change resets the social hierarchy, re-running the underdog loop at new scale (the
humiliation-comeback beat is renewable per tier [R]). (c) **Resource-economy subgame:**
acquisition arcs (pills, artifacts, techniques) fill inter-breakthrough chapters.

**3. Reader-bond devices.** Interiority: strategic monologue (plans, risk assessment) —
closer to mystery than battle. Visual token: the technique signature / artifact. Failure
cadence: frequent early-tier humiliations, near-zero late-tier losses — the genre
*intentionally* decays failure over the run, trading tension for wish-fulfillment
momentum (accepted by its audience; alien to JP-genre norms [C]).

**4. Anti-patterns (documented).** Tier inflation without social re-anchoring (numbers
with no face-stakes = drop [R bible]). Forgetting the mortal self (the MC becomes an
unreadable god). JP-import moral clarity breaking face-culture logic (the bible's named
localization hazard [R]). Pacing collapse from resource-subgame bloat [C].

**5. Wellness-embed note.** Vessel: `cultivation_martial.teacher` — "the master of the
lower gate" (dantian knows first; force ruptures [R]). Eastern-somatic payloads (qi,
breath, grounding) are genre-native (`qi_foundation`, `warrior_calm` brands [R]).
Contract break: doctrine that disputes the genre's ambition frame instead of grounding it.

**Confidence: medium** — mechanics are uniform across the canon but CN market data is
opaque relative to Oricon/Circana (the bible carries the same caveat [R]).

---

## mecha — Mecha (mecha bible)

**Exemplars:** Shinji Ikari (*Evangelion* — 14-vol manga + the $16B franchise the
portfolio plan cites as the genre's wellness proof [R]). Amuro Ray (*Mobile Suit Gundam*
lineage — 45+ years of franchise renewal via pilot-generation handoff; Gunpla economics
repo-cited [R]). Suletta Mercury (*The Witch from Mercury* — best-selling Gunpla
generation of its era [R]; the current-decade bond proof). Nagate Tanikaze (*Knights of
Sidonia* — 15 vols, completion model [K]).

**1. Trait architecture.** Want: pilot well / be needed. Need: co-regulation — the mecha
MC's body is the instrument the machine amplifies (Shinji's sync-rate literalizes
nervous-system state as combat stat [R bible]). Competence: piloting talent wrapped in
psychological fragility — the genre uniquely permits a *low-resilience* MC. Moral
clarity: medium; command structures are morally compromised by design. Register: interior,
pressurized, hardware-precise.

**2. Endurance mechanics.** (a) **Franchise-generational handoff:** mecha endures at the
FRANCHISE level (Gundam's pilot-per-era), not the single-MC level — plan series as
bounded pilots inside a persistent world/hardware lineage. (b) **Sortie episodics:**
mission structure gives chapter units; escalation is hardware+stakes, not power-ups.
(c) **Machine-relationship serial:** the pilot-machine bond deepens like a romance ladder
(sync, refit, loss of the machine as amputation).

**3. Reader-bond devices.** Interiority: highest of the action genres — cockpit monologue
under g-force is the signature surface (interaction grammar: cockpit fit, human return
after action [R]). Visual token: the machine itself (the MC's silhouette is the mecha).
Failure cadence: sorties fail often; comrades die; the machine is destroyed/rebuilt —
loss is hardware-mediated and thus survivable-but-costly.

**4. Anti-patterns (documented).** The unbothered ace (removing fragility removes the
genre's psychological core). Hardware porn without body cost (the bible's failure list:
the pilot must physically pay [R]). Command-structure cartoon-villainy (parallels
workplace). Franchise reboot fatigue — new generation without new thesis [C].

**5. Wellness-embed note.** Vessel: `mecha.teacher` — "the mechanic who co-regulates the
pilot" (A-grade gold exemplar [R]). Depression/burnout-as-sync-failure is the portfolio
plan's flagship embed (Evangelion register [R]). Contract break: the machine fixing the
feeling — regulation must happen in the body first, machine second.

**Confidence: high** (franchise economics repo-pinned [R]).

---

## sci_fi_cyberpunk — Sci-Fi / Cyberpunk (sci_fi_cyberpunk bible)

**Exemplars:** Motoko Kusanagi (*Ghost in the Shell* — the franchise-endurance template
for the family [R][K]). Senku Ishigami (*Dr. Stone* — 26 vols, ~15M; the science-ladder
shonen straddle [K]). Killy (*BLAME!* — 10 vols; the wordless-quest template [K]).
Kaneda & Tetsuo (*Akira* — 6 vols; the completion-model masterpiece [K]).

**1. Trait architecture.** Want: the answer/the exit/the network. Need: confirm the self
is still there under the augmentation (identity-under-system is the family's invariant
[R bible]). Competence: system-literacy (hacking, science, navigation) — the MC reads
the world's code. Moral clarity: medium-low; systems implicate everyone. Register: cool
surface, existential interior.

**2. Endurance mechanics.** (a) **Franchise/iteration endurance** (GitS: films, series,
manga iterations re-ask one question with new tech) — like mecha, the family renews at
franchise level; single runs are bounded (Akira's 6 vols). (b) **Science/tech ladder**
(Dr. Stone): each invention is a rung with visible societal delta — the family's best
pure-serial engine. (c) **Descent/architecture episodics** (BLAME!): spatial progression
substitutes for character progression.

**3. Reader-bond devices.** Interiority: philosophical monologue rationed against action;
the body-check beat (am I still me?) recurs as the family's signature interior gesture.
Visual token: the interface/implant/lab gear. Failure cadence: pyrrhic — victories
routinely cost identity ground; the family's bond is unease, not triumph.

**4. Anti-patterns (documented).** "Neon wallpaper" — the excellence gate's own banned-
evidence phrase for this family [R]: aesthetic without system-stakes. Techno-lecture
drift (exposition replacing story — bible failure list [R]). Identity question resolved
too early (the engine is the unresolve). Body-horror escalation without meaning
(parallels horror's gore trap).

**5. Wellness-embed note.** Vessel: `sci_fi_cyberpunk.teacher` — "the wetware elder"
(trust the meat's alarm over the feed [R]). Digital-burnout payloads are the
`digital_ground` brand's anchor (the developer who optimized everything except
themselves [R]). Contract break: digital-detox sermon; the doctrine must stay embodied
(the body's alarm, not an app-blocker moral).

**Confidence: high** on craft; medium on current JP-print commercial weight (family is
franchise/anime-led, thin on 2024–26 Oricon print charts [R][W]).

---

## supernatural_everyday — Supernatural Everyday

**Exemplars:** Takashi Natsume (*Natsume's Book of Friends* — 31+ volumes over 20+
years, 15M+; the genre's endurance definition [K]). Kimihiro Watanuki (*xxxHOLiC* — 19
vols + sequels [K]). Chise Hatori (*The Ancient Magus' Bride* — 5M+ repo-cited, 20+
vols [R][K]). Ginko (*Mushishi* — straddle with healing [K]). Momo & Okarun (*Dandadan*
— the high-energy modern straddle [W][R]).

**1. Trait architecture.** Want: quiet coexistence (return the names, serve the shop,
finish the contract). Need: belonging among humans — the genre's MCs can see what
others can't and are therefore lonely among people; the spirit world is where they're
competent, the human world is where they're needy. Competence: boundary-literacy
(rules, offerings, names). Moral clarity: high, mercy-forward. Register: melancholy-
warm, seasonal.

**2. Endurance mechanics.** (a) **Spirit-of-the-week with a debt spine:** the Book of
Friends structure — an inventory (names to return, price to pay, contract to serve)
that meters the serial while each chapter's spirit brings a complete human-shaped
wound. The debt inventory is the frozen spine done gently. (b) **Boundary-calendar
episodics:** festivals, seasons, thresholds supply occasions (interaction grammar:
liminal boundary, offering [R]). (c) **Found-family accretion** on the human side
paces the loneliness need glacially.

**3. Reader-bond devices.** Interiority: soft first-person melancholy; the genre's
signature beat is the spirit's grief rhyming with the MC's own unspoken one. Visual
token: the talisman/book/shop. Failure cadence: the MC often cannot save the spirit —
bittersweet release substitutes for victory (the genre's defining emotional cadence).

**4. Anti-patterns (documented).** Combat drift (escalating exorcism battles converts
the family into battle-genre and loses its audience [C, uniform]). Debt-spine spending
(returning names too fast). Spirit-rule inconsistency (fair-play for the veil).
Loneliness cured early (the need must outlast the run).

**5. Wellness-embed note.** Vessel: `supernatural_mystery.teacher` — "the medium who
reads the cold" (body signal before the ghost [R]). Grief/boundary payloads are anchor
embeds (`spiritual_ground`, `stillness_press` rows [R]): the spirit's unfinished
business IS grief work, offerings ARE boundaries. Contract break: exorcising the
metaphor (naming the spirit as anxiety on the page).

**Confidence: high.**

---

## school — School / Youth (school_coming_of_age lane)

**Exemplars:** Shoko Komi (*Komi Can't Communicate* — 37 vols, 10M+; social-anxiety-as-
premise, the family's most on-mission proof [K]). Taiki Inomata (*Blue Box* — Oricon
top-10 2024 [R], 2.39M in 2025 [W]; sports×school×romance braid). Eikichi Onizuka
(*GTO* — 50M franchise; the teacher-POV variant [K]). Nagisa & class (*Assassination
Classroom* — 25M, 21 vols; the bounded-cohort completion model [K]).

**1. Trait architecture.** Want: survive/win the school-shaped test (exam, club,
confession). Need: an identity that exists outside the peer-group's read of them
(interaction grammar: inside/outside group position [R]). Competence: one pocket of
mastery invisible to the school's status system. Moral clarity: high; cruelty is
environmental, not villainous. Register: earnest with comic weather.

**2. Endurance mechanics.** (a) **The calendar is the engine:** terms, festivals,
exams, tournaments — school supplies a repeating occasion ladder that renews for
exactly as long as enrollment lasts. (b) **The graduation ceiling is REAL:** school
series are bounded by design (Assassination Classroom ends at graduation); long runs
either braid a second engine (Blue Box's sports bracket) or rotate cohorts (GTO's
class-of-the-year). Plan bounded. (c) **Premise-as-need** (Komi): making the wellness
condition itself the premise gives every chapter a micro-goal (one more friend).

**3. Reader-bond devices.** Interiority: high — adolescent over-reading of tiny social
signals is the genre's native surface. Visual token: uniform variation, the desk, the
rooftop. Failure cadence: frequent small social failures, one big rationed set-piece
failure per term (the failed festival, the lost tournament).

**4. Anti-patterns (documented).** Adult-voiced teens (register break). The frozen
third year (refusing graduation past reader patience — the family's version of the
frozen-spine overdraft [C]). Bullying aestheticized without cost (reader-safety norm
[R shojo parallel]). Premise-condition cured off-page (Komi's craft is on-page
increments).

**5. Wellness-embed note.** Vessel: `school_coming_of_age.teacher` — "the senpai who
pays quiet attention" (being seen accurately, no speeches [R]). Study-anxiety/identity
payloads are anchor embeds (`calm_student` brand [R]). Komi proves the strongest form:
the condition as premise, dignified, incremental. Contract break: the counselor scene.

**Confidence: high.**

---

## memoir — Memoir / Life Reflection (josei_adult_memoir bible)

**Exemplars:** Nagata Kabi (*My Lesbian Experience with Loneliness* + 5 sequels — the
serialized-self endurance model [K]). Shigeru Mizuki (*Showa: A History of Japan* /
*Onward Towards Our Noble Deaths* — the witness-memoir monument [K]). Marjane Satrapi
(*Persepolis* — 2M+ copies; the graphic-memoir crossover proof [K]). Alison Bechdel
(*Fun Home* — the US literary-memoir standard, Broadway-adapted [K]).

**1. Trait architecture.** The MC is the **author-persona at a distance** — memoir's
defining trait is the gap between narrating-self (now, wiser, wry) and experiencing-
self (then, raw). Want (then): survive the period recounted. Need (now): make it mean
something. Competence: observational honesty; the persona's flaws are the material.
Moral clarity: confessional — the persona indicts itself first. Register: caption-led,
essayistic (bible: diaristic, resists transformation arcs [R]).

**2. Endurance mechanics.** Like essay, memoir is **completion-first at the work level,
persona-serial at the career level**: Nagata Kabi's sequel-per-life-event and Mizuki's
era-by-era output show the form's endurance is the trusted narrating voice, not an
open serial. The bible's 48-vol shape (12-yr diaristic window with scheduled
retrospectives [R]) formalizes this: plan life-quarters, not arcs.

**3. Reader-bond devices.** Interiority: total, doubled (then-feeling + now-comment).
Visual token: the self-caricature avatar (Kabi's pink sketch-self; Mizuki's cartoon
self against realist war art — the style gap IS the device). Failure cadence:
continuous; memoir's bond is surviving failure into testimony.

**4. Anti-patterns (documented).** The triumphant-recovery arc (bible: the form
resists transformation [R]; a cure ending falsifies the genre). Score-settling
(memoir that prosecutes others loses the confessional license). Persona drift across
sequels. Privacy collapse — real-person collateral damage is the family's specific
ethical/legal hazard [C].

**5. Wellness-embed note.** No dedicated vessel; memoir is the ONLY family where the
teacher may be the page itself (the narrating voice legitimately concludes). For
Phoenix (teacher-brand context): memoir-register series must still keep the brand
teacher unnamed per the hard rule [R] — the narrating persona is a character author,
not the brand teacher (Manga Author System memory).

**Confidence: high.**

---

## social_issue — Social Issue / Josei Realism

**Exemplars:** Sachiko Azuma (*With the Light: Raising an Autistic Child* — 15 vols,
serialized 2000s josei; the family-facing social-issue standard [K]). Tsugumi Aikawa
(*Perfect World* — 12 vols; disability romance with documented advocacy reception
[K]). Shoya & Shoko (*A Silent Voice* — 7 vols, 3M+; bullying/deafness [K]).
Retsuko/workplace straddles for labor-issue register [R].

**1. Trait architecture.** Want: navigate the institution (school, welfare, workplace,
care system) for a concrete outcome. Need: be seen as a person, not a case. The MC is
often a **dyad: the affected person + the carrying person** (mother/child,
partner/partner) — the interaction grammar's care-network frame [R]. Competence:
learned-by-necessity institutional literacy. Moral clarity: high empathy, low
preachiness when done right. Register: grounded realism (visual grammar row [R]).

**2. Endurance mechanics.** (a) **The institution supplies stages:** diagnosis →
school-entry → employment → independence (With the Light ran 15 volumes on the child's
life-stage ladder). (b) **Case-plus-continuity braid:** each volume handles one
institutional encounter completely while the family's own arc advances. (c) Bounded by
honesty: the family resists indefinite serialization; plan life-stage arcs.

**3. Reader-bond devices.** Interiority: the carrying person's exhausted, precise
voice. Visual token: the document/form/threshold (interaction grammar: access barrier
[R]). Failure cadence: institutional defeats are frequent and realistic; wins are
partial — the genre's credibility (and advocacy power) depends on refusing fantasy
fixes.

**4. Anti-patterns (documented).** The poster problem (interaction grammar: "do not
turn the issue into a poster" [R]). Inspiration-porn framing (the affected person as
lesson-object). Villain-institution cartoonery (parallels workplace). Cure endings.
Research thinness — the audience includes the people depicted; error is harm [C].

**5. Wellness-embed note.** No dedicated vessel; nearest = `workplace_drama.teacher`
custodian-figure generalized to the veteran navigator (the parent three years ahead
in the same system). Payloads (caregiver burnout, self-worth) are native. Contract
break: the MC's story becoming the brand's pamphlet.

**Confidence: medium** — commercial ceiling of the family is real but modest; craft
extraction is solid, market mass is thin [R allocation doc: 1% empirical share].

---

## graphic_medicine — Graphic Medicine / Therapeutic Essay

**Exemplars:** White Blood Cell U-1146 & Red Blood Cell AE3803 (*Cells at Work!* —
13M+ franchise; the body-anthropomorphized education-entertainment proof [K]). Black
Jack (procedural straddle — the surgeon-witness [K]). Brian Fies (*Mom's Cancer* —
the Eisner-winning patient/caregiver memoir standard [K]). Nagata Kabi (memoir
straddle — hospitalization volumes [K]).

**1. Trait architecture.** Three viable MC shapes: (a) the anthropomorphized body-
agent (Cells at Work — the body as workplace ensemble); (b) the clinician-witness
(Black Jack pattern); (c) the patient/caregiver-narrator (memoir pattern). Want:
this crisis survived / this shift completed. Need: agency inside a body/system that
doesn't ask permission. Moral clarity: high. Register: either bright-educational or
confessional-precise; both require **medical accuracy as a hard contract**.

**2. Endurance mechanics.** (a) **The body is an infinite case generator** (Cells at
Work: pathogen-of-the-week, plus spinoffs per organ-system — franchise endurance via
body-map rotation). (b) Clinician-witness inherits the procedural's client-transfer
engine. (c) Patient-narrator inherits memoir's completion-first shape. Phoenix fit:
(a) is the scalable engine; (b)/(c) are bounded prestige lanes.

**3. Reader-bond devices.** Interiority: the body-agent's earnest shop-floor voice /
the patient's chart-precise dread. Visual token: the cell uniform, the chart, the IV
stand (interaction grammar: care artifact + patient agency [R]). Failure cadence:
crises recur honestly (cancer arcs in Cells at Work kill cells the reader loved) —
the family teaches loss inside education.

**4. Anti-patterns (documented).** Medical error (the hard contract; expert audience
+ real-world stakes). False-hope arcs (parallels social_issue's cure ban). Body-
shame framing (the body must stay the protagonist's home, not the enemy — matches
the portfolio plan's somatic embed rule [R]). Lecture drift (education must ride
character stakes — Cells at Work's craft [C]).

**5. Wellness-embed note.** No dedicated vessel; this family is the portfolio's most
literal wellness shell (`bio_flow` brand: "Cells at Work register with darkness"
[R]). Somatic payloads are the premise itself. Contract break: diagnosis language
aimed at the READER (the story may diagnose a cell, never the audience).

**Confidence: medium-high** — Cells at Work anchors commercially; the family's other
lanes are prestige-scale.

---

## battle_internal — Internal Battle / Philosophical

**Exemplars:** Shigeo "Mob" Kageyama (*Mob Psycho 100* — 16 vols + hit adaptations;
the emotion-gauge-as-power-system template, the family's defining modern work [K]).
Bojji (*Ranking of Kings* — 5M+; the gentle-strength template [K]). Punpun (essay
straddle — the cautionary maximal case [R][K]). Thorfinn (historical straddle — the
vow-arc as internal battle [R]).

**1. Trait architecture.** Want: control/suppress the inner force (power, rage,
grief, weakness). Need: befriend it — the family's invariant arc is suppression →
integration. Competence: enormous latent power with deliberately weak social
competence (Mob can level cities but can't confess to a girl; Bojji is deaf-frail
royalty with hidden mastery). Moral clarity: high-empathy; the antagonist is usually
a mirror-self or a philosophy (interaction grammar: self-shadow, moral counterpart
[R]). Register: quiet with rationed eruptions.

**2. Endurance mechanics.** (a) **The gauge:** Mob's ???% meter converts internal
state into a visible, renewable escalation clock — each arc charges and discharges
it differently; this is THE machine-readable form of emotion-as-plot. (b) **Mirror
rotation:** each arc supplies a counterpart embodying one mis-relation to power
(suppressor, indulger, exploiter). (c) Bounded by integration: once the self is
befriended the engine completes (Mob ends at 16 vols) — plan mid-length, not 100+;
100+ endurance requires braiding a second engine (Thorfinn's historical ladder).

**3. Reader-bond devices.** Interiority: the gap between placid surface and roaring
interior (drawn, not narrated — Mob's blank face vs psychic storms). Visual token:
the gauge/percentage, the shadow-self design. Failure cadence: external losses are
rare; **internal losses (eruptions, suppressions that hurt someone) are the cadence**
— roughly one per arc, each converting to integration progress.

**4. Anti-patterns (documented).** The eruption as pure victory (if losing control
wins fights cost-free, the thesis dies). Philosophy monologue replacing dramatized
struggle (dark_fantasy §6 item 2 applies verbatim [R]). Suppression glorified
(the family's ethic requires integration, not conquest of self). Gauge inflation
(resetting the meter arbitrarily breaks its honesty [C]).

**5. Wellness-embed note.** No dedicated vessel needed — battle_internal is the
closest existing shell to explicit emotional-regulation content while staying story:
the gauge, the shadow-self, and the mirror-antagonist are ready-made embed
apparatus (canonical fallback engines already name conviction/reflection [R]).
Contract break: therapy vocabulary attached to the gauge.

**Confidence: high.**

---

## Cross-family synthesis (for planners + Lane 07)

1. **Endurance engines come in exactly four shapes** across all 25 families: the
   *renewable ladder* (bracket/tier/org-chart/map/calendar), the *episodic case
   engine* (world supplies complete units; MC stasis is a feature), the *frozen
   serial spine* (one unresolvable question rationed for years), and the
   *relationship accretion engine* (cast growth hosts future arcs). Every 100+
   episode series in this study runs at least two simultaneously; most failures
   are one engine over-spent.
2. **Failure cadence is a genre signature, not a universal:** sports/comedy MCs
   lose constantly, mystery/procedural MCs almost never lose the case but lose the
   personal frame, dark_fantasy converts wins into costs, healing replaces losses
   with regret beats. Gating "the MC must fail sometimes" globally would be wrong;
   the checklist encodes it per-family.
3. **Completion-first families exist:** essay, memoir, school, battle_internal,
   social_issue (and single-run mecha/sci-fi works) endure at the persona,
   franchise, or cohort level, not the single-serial level. Series planners must
   not force 100+ episode shapes onto them.
4. **The wellness contract is uniform:** every family tolerates the payload only
   while it stays enacted (body, object, method, relation) and breaks the moment
   it is named on the page. This is the same rule as the teacher hard rule
   (`teacher_apparatus_per_genre.md`) and the excellence gate's banned-evidence
   phrases — the checklist repeats it per-family as a testable anti-pattern.

## Sources

**Web-verified this lane (2026-07-24):**
- Oricon 2026 first-half series ranking (Frieren #1 1.62M; One Piece #2 1.60M; JJK #3 1.43M;
  Blue Lock #4 1.27M; Chainsaw Man #5 1.15M; JJK Modulo 1.14M):
  https://www.resetera.com/threads/oricon-japan-manga-sales-2026-first-half-2025-nov-17-2026-may-17-frieren-1-chainsaw-man-and-jujutsu-kaisen-hang-around-after-their-end.1529503/
- ICv2 / Circana BookScan monthly Top-20 manga Feb–Jun 2026 (JJK dominance; Apothecary
  Diaries vol 1 charting): https://icv2.com/articles/markets/view/61902/ ·
  https://icv2.com/articles/markets/view/62141/ · https://icv2.com/articles/markets/view/62437/ ·
  https://icv2.com/articles/markets/view/62648/ · https://icv2.com/articles/markets/view/62885/
- CBR "The 10 Highest-Selling Manga of 2026" (JJK 150M cumulative; Kingdom 120M; Blue Lock
  50M; Apothecary 45M; Frieren 35M+; CSM 36M; Fragrant Flower 2.04M/10M+; Blue Box 2.39M;
  Tougen Anki 6M): https://www.cbr.com/official-highest-selling-manga-of-2026-ranked/
- AJPEA via ANN: Japan manga market 2025 = ¥692.5B, −1.7% (first contraction since 2017);
  digital ¥527.3B (+2.9%, 76.1% share); print volumes ¥126B (−14.4%):
  https://www.animenewsnetwork.com/news/2026-03-03/manga-market-in-japan-shrinks-for-1st-time-in-7-years-in-2025/.234838
- WEBTOON Entertainment FY2025: revenue $1.4B (+2.5%; +3.9% cc), IP adaptations +31.8%,
  operating loss narrowed to $63.5M:
  https://ir.webtoon.com/news-releases/news-release-details/webtoon-entertainment-inc-reports-fourth-quarter-and-full-year-0
- Webtoon genre shares 2025 (romance ≈27.4% #1; fantasy ≈21.6% fastest-growing):
  https://market.us/report/webtoons-market/
- Kagurabachi: 4M+ circulation incl. digital; indefinite hiatus from June 2026; anime
  April 2027: https://essential-japan.com/news/shonen-jump-announces-indefinite-hiatus-for-kagurabachi-manga/ ·
  https://www.thepopverse.com/comics-kagurabachi-release-date-schedule-shueisha-weekly-shonen-jump-new-chapters
- Golgo 13 Guinness record, 201 volumes; Kochikame 200 volumes (1976–2016):
  https://www.animenewsnetwork.com/interest/2021-07-05/golgo-13-manga-breaks-guinness-world-record-for-most-volumes/.174827

**Repo-pinned:** `popular_genre_ranking_2026-05-02.md`,
`marketing_grounded_per_genre_allocation_2026-05-13.md`, `GENRE_PORTFOLIO_PLAN.md`,
craft bibles §5/§6/§7, `teacher_apparatus_per_genre.md`, `manga_mode_vessels.yaml`,
`main_character_interaction_grammar_by_genre.md`, `story_excellence_gates.yaml`.

**[K]-class facts:** circulation/volume/run-length figures as publicly reported by
publishers and Oricon and mirrored on Wikipedia (per-series pages); marked [K] inline.

*End of manga_mc_endurance_study_2026-07-24.md.*
