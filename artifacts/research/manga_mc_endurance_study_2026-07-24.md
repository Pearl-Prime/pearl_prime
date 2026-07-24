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
