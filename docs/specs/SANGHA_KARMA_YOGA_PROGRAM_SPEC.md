# Sangha Karma Yoga — V1 program spec

**Status:** ACTIVE — RATIFIED 2026-06-11. All open Q-SKY-* resolved to recommended defaults (§13) per operator green-light, EXCEPT **Q-SKY-LEGAL-01 = DEFERRED** (profit-share legal vehicle requires legal counsel; the operator-locked 1%-per-active-contributor mechanism stands as placeholder, no allocation paid until counsel confirms the vehicle). Ratification logged OPD-20260611-056 (batch) + OPD-20260611-057 (LEGAL deferred). Cap `SANGHA-KARMA-YOGA-V1-01` → ACTIVE.
**Cap entry:** `SANGHA-KARMA-YOGA-V1-01` in `docs/PEARL_ARCHITECT_STATE.md`
**Project:** `PRJ-SANGHA-KARMA-YOGA-V1` in `artifacts/coordination/ACTIVE_PROJECTS.tsv`
**Subsystem:** `sangha_program` (new — `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`)
**Owner (spec ratification):** Pearl_Architect
**Program lead (operations):** Operator (Ahjan)
**Drafted:** 2026-06-09

**Authority + source documents:**

- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PEARL_ARCHITECT_STATE.md` (precedent cap entries `MUSIC-MODE-BRAND-INTEGRATION-V1-01`, `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01`)
- `old_chat_specs/USLF_3_LA.txt` (operator's canonical transcript, USLF #3 Los Angeles)
- `pearl_news/config/teacher_news_roster.yaml` (master roster — Joshin Shingon lineage)
- `docs/migrations/JOSHIN_SHINGON_KENJIN_ZEN_MIGRATION_PLAN_2026-05-18.md` (Joshin = Shingon, NOT Zen — already-ratified migration)
- `SOURCE_OF_TRUTH/teacher_banks/` (16 teacher banks including `master_feung`, `master_sha`, `master_wu`, `joshin`, `sai_ma`, `pamela_fellows`)
- `./teachers/ahjan/intake/Dharma Talks/` (23 Sangha-related operator dharma talks, 2018–2022)
- `docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md` (Pillar P2 cross-ref)
- `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md` (Pillar P1 cross-ref)
- `docs/PEARL_NEWS_WRITER_SPEC.md` (Pillar P3 cross-ref)
- `BRAND_ADMIN_CANONICAL_PACKAGE.md` (Pillar P6 cross-ref)
- `docs/FULL_FUNNEL_PLAN.md` (Pillar P7 cross-ref)
- `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` (Sangha brand storefront destination)
- `config/manga/canonical_brand_list.yaml` (Path X 37 — read-only boundary)
- `CLAUDE.md` (LLM Tier policy — Tier 1 only this session; no paid APIs)

---

## §1. Purpose

This program structures **Sangha Karma Yoga** — a volunteer service pathway for sangha members who want to participate in the operator's mission to *uplift the world with the alliance of these great masters through offering content*.

The frame is operator-given. The operator has been teaching karma yoga and sangha unity to his sangha for at least four years (`./teachers/ahjan/intake/Dharma Talks/2021-10-16_All-Sangha-Satsang_Karma-Yoga.txt`; `./teachers/ahjan/intake/Dharma Talks/2022-01-22_Sangha-Unity-Teaching-&-New-Org-Structure.txt`). This spec formalizes program structure around that existing teaching.

The mission backbone is named in operator's own voice in `old_chat_specs/USLF_3_LA.txt`:

> *"Our mission is to help the world by helping to change the youth, the young people. If you could give them support, help them in their troubles as they grow, then the … if we can help millions of children around the world, it changes the world as they grow."*

Sangha Karma Yoga is **how that mission becomes load-bearing** — by structuring sangha members into 7 work pillars, anchored by 1 weekly Sunday Zoom coordination call + quarterly spiritual offerings.

---

## §2. Karma Yoga — brief framing

The sangha already knows what karma yoga is. This program does not re-teach it; it offers a structured field for it.

Karma yoga here means: *service as practice*. Work done in dedication to the mission, with attention given to the inner state of the doer, not just the outer outcome.

The 7 pillars are containers for that practice. Sunday coordination is collective accountability. The quarterly offerings (master teachings + Pearl empowerments) are dharma support — gifts that flow back to those who serve, not transactional rewards.

The dharma source for that framing is operator-given. The operator's `2021-10-16_All-Sangha-Satsang_Karma-Yoga-&-Past-Life-Seeing.txt` is the canonical voice. This spec defers to it.

---

## §3. The 7 work pillars

Operator-named, ordered for the brochure. Each pillar shadows specific Pearl_* agents but is operated by human sangha karma yogis under a **Dharma Steward** (pillar lead).

### §3.1 Pillar P1 — Pearl Prime contributor pool
**Work:** Contribute to Pearl Prime book authoring — atom authoring, story-cell authoring, gratitude practices, teacher-doctrine cleanup, persona × topic atom backfill. Shadows: **Pearl_Editor + Pearl_Writer + Pearl_Prime**.
**Authority docs:** `docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md`, `specs/PHOENIX_V4_5_WRITER_SPEC.md`.
**Weekly heartbeat:** atom-authoring rate; teacher-bank backfill completions; bestseller-smoke pass rate.
**Shipped definition:** atoms merged to `SOURCE_OF_TRUTH/teacher_banks/<teacher>/approved_atoms/` and visible in catalog-quality scoring.
**Reward tier:** **Tier I (profit-share — 1% of Pearl Prime income)** + Tier II spiritual access.

### §3.2 Pillar P2 — 48 Social contributor pool
**Work:** Author, schedule, audit, and tune 48 Social distribution — short-form clip selection, social CTA copy, hook authoring, platform-specific formatting. Shadows: **Pearl_Marketing**.
**Authority docs:** `docs/48_SOCIAL_GHL_BRAND_ADMIN_SPEC.md`, `docs/FULL_FUNNEL_PLAN.md`.
**Weekly heartbeat:** posts shipped per platform; CTR + opt-in rate; new-subscriber attribution by post.
**Shipped definition:** post live on platform with attribution tag; conversion measured ≥7 days post-publish.
**Reward tier:** **Tier I (profit-share — 1% of Pearl Prime income)** + Tier II spiritual access.

### §3.3 Pillar P3 — Pearl News contributor pool
**Work:** Pearl News article authoring, fact-checking, locale review, daily packs, teacher-attribution validation. Shadows: **Pearl_News**.
**Authority docs:** `docs/PEARL_NEWS_WRITER_SPEC.md`, `docs/research/PEARL_NEWS_QWEN_DEEP_RESEARCH_ENGINE.md`.
**Weekly heartbeat:** articles shipped per locale; teacher-attribution accuracy; daily-pack QA pass rate.
**Shipped definition:** article published to live Pearl News surface with passing QA gates.
**Reward tier:** **Tier I (profit-share — 1% of Pearl Prime income)** + Tier II spiritual access. *(Pillar P3 is in Tier I under the operator-ratified universal-pillar mechanism — supersedes earlier draft framing.)*

### §3.4 Pillar P4 — United Spiritual Leaders Forum (USLF) administration
**Work:** Coordinate the forum cadence (currently in-person events; USLF #2 was Koyasan, #3 was Los Angeles per `old_chat_specs/USLF_3_LA.txt`). Master scheduling, panelist coordination, recording, translation, distribution to Pearl News + Pearl Prime + 48 Social. Shadows: **Pearl_PM + Pearl_Prez + Pearl_Localization**.
**Authority docs:** `old_chat_specs/USLF_3_LA.txt` (operator's canonical voice), `pearl_news/config/teacher_news_roster.yaml`.
**Weekly heartbeat:** forum planning cycle progress; master availability matrix; downstream distribution status.
**Shipped definition:** forum recorded, translated, and lit up across at least one downstream surface (Pearl News article OR Pearl Prime book lane OR 48 Social clip stream).
**Reward tier:** Tier I (1% of Pearl Prime income) + Tier II spiritual access + Tier III recognition for sustained service.

### §3.5 Pillar P5 — United Nations Spiritual Alliance for Youth (UNSAY) administration
**Work:** UNSAY-specific youth-outreach administration. Per Q-SKY-UNSAY-NAMING-01, naming + scope confirmation pending from operator. Working assumption: UNSAY is the youth-outreach extension of USLF, addressing the operator-stated mission to *"help the world by helping to change the youth"*. Shadows: **Pearl_Marketing + Pearl_Prez**.
**Authority docs:** TBD pending operator confirmation (placeholder under this spec).
**Weekly heartbeat:** TBD per Q-SKY-UNSAY-SCOPE-01.
**Shipped definition:** TBD per Q-SKY-UNSAY-SCOPE-01.
**Reward tier:** Tier I (1% of Pearl Prime income) + Tier II spiritual access + Tier III recognition.

### §3.6 Pillar P6 — Sangha brand administrators
**Work:** Run a Sangha-themed book lane as a brand administrator — composite teachings from the alliance of masters, CTAs to Sangha materials + free meditations, onboarding funnels for new students. One Sangha karma yogi per brand lane. Shadows: **Pearl_Prez + Pearl_Brand + Pearl_Marketing**.
**Authority docs:** `BRAND_ADMIN_CANONICAL_PACKAGE.md`, `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md`, `config/brand_registry.yaml`, `config/brand_author_assignments.yaml`.
**Weekly heartbeat:** brand-lane book throughput; freebie + funnel conversion; storefront listing health.
**Shipped definition:** Sangha-themed book lane producing on cadence with healthy funnel + active storefront listing.
**Reward tier:** Tier II spiritual access + **Sangha Author credit (Tier III recognition)** on every book published in the lane.
**Deep-dive:** see §8.

### §3.7 Pillar P7 — Sangha new-student onboarding ops
**Work:** Run the funnel mechanics from Sangha brand discovery through to in-sangha membership — discovery copy, intake form, first-conversation protocols, hand-off into the sangha proper. Shadows: **Pearl_Marketing + Pearl_Prez**.
**Authority docs:** `docs/FULL_FUNNEL_PLAN.md`, `funnel/`, `config/freebies/`.
**Weekly heartbeat:** intake form completions; first-conversation completion rate; sangha-handoff conversion.
**Shipped definition:** new student attended one sangha event after intake, with consent recorded.
**Reward tier:** Tier I (1% of Pearl Prime income) + Tier II spiritual access + Tier III recognition.

---

## §4. Role ladder

Roles are dharma-shaped, not corporate-shaped. Movement up the ladder happens by sustained service, not application.

| Role | What it is | How you arrive |
|---|---|---|
| **Karma Yogi** | Any active sangha volunteer in any pillar | Opt-in via §9 onboarding flow + first Sunday attended |
| **Dharma Steward** | Pillar lead; coordinates one pillar's weekly heartbeat | Nomination by current Dharma Stewards + operator confirmation (initial 7 nominated by operator post-merge per Q-SKY-PILLAR-LEAD-INITIAL-01) |
| **Sangha Author** | Brand administrator running a Sangha-themed book lane (P6) | Sustained service ≥ 1 quarter as Karma Yogi + invitation by P6 Dharma Steward + operator confirmation |
| **Pearl Empowered** | Recognized lineage milestone — received first Pearl empowerment from Ahjan | 90-day milestone OR quarterly group ceremony attendance (per Q-SKY-PEARL-EMPOWERMENT-CADENCE-01). Recognition of lineage, not hierarchy promotion. |
| **Cross-pillar Coordinator** | Optional rotating role bridging 2-3 pillars; pulls Sunday agenda items together | Quarterly rotation; nominated by Dharma Stewards |

**Anti-drift:** The Pearl Empowered designation is **lineage recognition**, not a management promotion. A Pearl Empowered Karma Yogi remains a Karma Yogi; the empowerment is a milestone of dharma transmission, not a rank.

---

## §5. Sunday Zoom meeting structure

**Cadence:** Weekly, Sundays. Default time: 9:00–10:00am PT / 5:00pm UTC (Q-SKY-SUNDAY-TIME-01).
**Length:** 60 minutes (Q-SKY-SUNDAY-LEN-01).
**Voice:** Coordination, not teaching. The teaching cadence is handled by the sangha's existing weekly + monthly classes — this Sunday is for the *work* of the karma yoga.

### §5.1 Agenda

| Block | Time | What |
|---|---|---|
| **Opening dharma reflection** | 5 min | A Dharma Steward (rotating) offers a brief reflection from the operator's teachings or the master alliance. Not a class — an anchoring. |
| **Pillar heartbeat reports** | 15–20 min | Each Dharma Steward reports what their pillar shipped this week. 2 minutes per pillar × 7 = 14 min target; if a pillar has nothing to report it says so. |
| **Cross-pillar issues + blockers** | 10 min | Anything where one pillar is waiting on another, or where two pillars are stepping on each other. Cross-pillar Coordinator (when seated) facilitates. |
| **Next-week commitments** | 10–15 min | Each pillar names what it intends to ship next week. Commitments are public so they can be tracked. |
| **Closing dedication** | 5 min | Brief closing offered by a different Dharma Steward than the opener. Reverent. |

### §5.2 Recording + async catch-up

Sunday Zoom is recorded. The recording is shared with all active Karma Yogis the same day. A short Sunday-notes doc (one paragraph per pillar + commitments list) is written by the Cross-pillar Coordinator (when seated) or rotating Dharma Steward and shared in the volunteer-only archive (Q-SKY-ARCHIVE-01).

Karma Yogis who cannot attend any given Sunday are still considered active if they read the notes + acknowledge commitments asynchronously.

---

## §6. Quarterly rhythm

This is the "extremely powerful, not extremely frequent" cadence.

**Each quarter contains:**

1. **One special teaching from a master in the alliance.** The operator-ratified Plan A master rotation (resolves Q-SKY-MASTER-ROTATION-01 + Q-SKY-MASTER-NAMING-01):

   | Quarter | Master | Tradition | Domain |
   |---|---|---|---|
   | Q1 | `master_feung` | Chinese wisdom / calligraphy / Hua Shan pilgrimage / Xi'an | Karma clearing via authentic presence (Grand Painting teaching) |
   | Q2 | `master_wu` | Taoist geomancy / Long Mai (Dragon Veins) / earth meridian / cross-regional | Ecological-harmony alignment via earth-meridian vessel |
   | Q3 | `junko` | New Age channeling / ascended masters / light language / cosmic council | Gen-Z / Alpha uplift via cosmic-council transmission |
   | Q4 | `joshin_sensei` (+ Ahjan Pearl Transmission) | Shingon Esoteric Buddhism / Dainichi Nyorai mandalas / Kōyasan / *Sokushin Jōbutsu* | Vairocana World Bodhisattva attainment in this very body |

   "Master Fan Zhou" in operator's spoken voice = canonical `master_feung` in repo (resolves naming reconciliation). Detailed per-quarter level definitions, attainment-state names, ritual ceremony shape, and Pearl News feedback-loop integration are specified in the V1.5 layer at `docs/specs/SANGHA_KARMA_YOGA_LEVEL_PROGRESSION_SPEC.md` (cross-link).
2. **One Pearl empowerment from Ahjan** — the operator's transmission work, named in his own voice in `old_chat_specs/USLF_3_LA.txt` line 177: *"Ajahn did his transmission work, uh, energy. It was beautiful. It was so strong."* Format per Q-SKY-PEARL-EMPOWERMENT-CADENCE-01: group ceremony quarterly + individual 90-day milestone for those completing first quarter active.

**Plus annually:**

3. **One in-person USLF retreat** — annual gathering. Active Karma Yogis are invited per Q-SKY-USLF-ACTIVE-DEF-01 default = 3 of 4 quarters active in the prior year. Travel: operator-discretion stipend per Q-SKY-STIPEND-01.

The quarterly + annual cadence is the **gift flow** — what comes back to those who serve. It is not contractual; it is dharma support. Frame language is humble per §15 anti-drift.

---

## §7. Reward tiers

The deck (file C) frames these as gifts received before they are responsibilities given. The spec records them as a structured tier system.

### §7.1 Tier I — Profit-share contributors (universal — any pillar qualifies)

**Operator-ratified mechanism (resolves Q-SKY-LEGAL-01 / Q-SKY-PROFIT-PCT-01 / Q-SKY-PROFIT-CAP-01 / Q-SKY-PROFIT-PEARL-NEWS-01 / Q-SKY-48-SOCIAL-BINDING-01 / GAP-SKY-06 in one stroke):**

**Who:** Any active Karma Yogi in **any** of the 7 pillars (P1–P7). Tier I is **not pillar-restricted**.

**Mechanism:**

- **Pearl Prime receives 5% of all-brand income** across the Phoenix Omega catalog (the operator's standing economics; pre-existing).
- **Active Karma Yogis each receive 1% of Pearl Prime's income** per quarter active.
- That is, each Karma Yogi's allocation = 1% × (5% × total brand income) = **0.05% of total brand income per active Karma Yogi per quarter**.
- "Active" per Q-SKY-PROFIT-PCT-01 default = 4+ Sundays attended in the quarter + ≥ 1 shipped deliverable in their pillar.
- **Qualifying work is universal**: a Karma Yogi serving in P4 USLF administration earns the same Tier I share as a Karma Yogi authoring atoms in P1 Pearl Prime. The pillars are dharma-equal under Tier I.
- **Layered with operator's pre-existing "10% to teachers" flow** (operator's LA transcript framing) — both flows operate; they apply to different parties.
- **Pillar P3 Pearl News + Pillar P4 USLF + Pillar P5 UNSAY + Pillar P6 Sangha brand admins + Pillar P7 Sangha onboarding all qualify** (resolves Q-SKY-PROFIT-PEARL-NEWS-01 by inclusion — Pearl News contributors are Tier I, not Tier II only).
- Legal counsel confirms the actual legal vehicle (distribution structure) before any allocation is paid. The percentage mechanism is operator-locked; the legal wrapper is the pending item under a now-narrowed Q-SKY-LEGAL-01.
- Tier I activation gated only on legal-counsel confirmation. The structural decision is closed.

### §7.2 Tier II — Spiritual access (all active Karma Yogis across all 7 pillars)

Available to every active Karma Yogi regardless of pillar:

| Offering | Cadence | Description |
|---|---|---|
| **Quarterly master teaching** | 4x / year | One master from the alliance offers a private teaching to the Karma Yogi cohort. Recorded for the volunteer-only archive (Q-SKY-ARCHIVE-01) with teacher's consent. |
| **Quarterly Pearl empowerment** | 4x / year | Group transmission ceremony from Ahjan. |
| **Annual in-person USLF retreat** | 1x / year | Active Karma Yogis invited; "active" per Q-SKY-USLF-ACTIVE-DEF-01. |
| **Volunteer-only archive of recorded teachings** | Continuous | Subject to teacher consent per recording per Q-SKY-ARCHIVE-01. |
| **Sangha Author credit** | Per book | Sangha Author role only; credit on every book published in their P6 brand lane. |

### §7.3 Tier III — Recognition (sustained service layer)

For Karma Yogis whose service crosses years:

- **Annual "Sangha Dharma Steward" titles** — recognition ceremony at the USLF retreat
- **Possible 1:1 time with masters** — operator-curated, not advertised as guaranteed (Q-SKY-1V1-MASTER-01)
- **Possible travel stipend for retreats** — case-by-case, operator-discretion (Q-SKY-STIPEND-01)
- **Sustained-service ribbon/inscription** mechanism — TBD per operator preference

**Anti-drift:** Tier III is recognition, not entitlement. The masters offering 1:1 time do so as gift, not obligation.

---

## §8. Sangha brand administrator pillar (P6) — deep dive

P6 is the largest pillar by headcount potential — many Karma Yogis can run Sangha-themed book lanes simultaneously, the same way the Pearl Prime brand-admin model already runs many lanes simultaneously (`BRAND_ADMIN_CANONICAL_PACKAGE.md`).

### §8.1 The Sangha brand definition

A **Sangha brand** is a book lane whose voice is composite — drawing from the alliance of masters rather than a single teacher. The teacher pool is the canonical master roster at `SOURCE_OF_TRUTH/teacher_banks/` (currently 16 banks: `adi_da, ahjan, joshin, junko, kenjin, maat, master_feung, master_sha, master_wu, miki, miyuki, omote, pamela_fellows, ra, sai_ma`).

Sangha brands differ from Path X brands in this composite-voice property. Path X 37 brands (`config/manga/canonical_brand_list.yaml`) are single-teacher-rooted; Sangha brands are alliance-rooted.

### §8.2 How a sangha member becomes a brand administrator

1. Karma Yogi for ≥ 1 quarter in any pillar
2. Express interest in P6 brand administration to current P6 Dharma Steward
3. Match to an open Sangha brand lane (or propose a new one; operator approves new Sangha brand naming)
4. 30-day orientation with P6 Dharma Steward shadowing
5. Brand lane goes live; Karma Yogi receives Sangha Author credit on first book published

### §8.3 The Sangha brand lane: composite teachings + CTAs

Each Sangha brand lane:

- Pulls teachings from ≥ 3 master banks (cross-referenced via `config/brand_author_assignments.yaml`)
- CTAs to Sangha materials (free meditations + new-student onboarding funnels — Pillar P7 cross-ref)
- Storefront destination: per `docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md` AMENDMENT-2026-06-04.2 — Sangha brands land in the same storefront with locale parity

### §8.4 Tooling reuse vs Sangha-new

| Surface | Existing (reuse) | NEW for Sangha |
|---|---|---|
| Brand registry | `config/brand_registry.yaml` extends with Sangha brand IDs | Sangha brand archetype flag (composite-voice = true) |
| Brand wizard | Existing wizard at `brand-wizard-app/` | Sangha mode option in step 1 mode selector (Q-SKY-WIZARD-MODE-01) |
| Atom routing | `phoenix_v4/planning/atom_router.py` | Cross-teacher atom blending policy (Q-SKY-COMPOSITE-VOICE-RULES-01) |
| Cover system | `config/authoring/author_cover_art_registry.yaml` | Sangha brand cover treatment (Q-SKY-SANGHA-COVER-TREATMENT-01) |
| Funnel + freebie | `funnel/`, `config/freebies/` | Sangha-themed freebies (Pillar P7 cross-ref; could ride existing freebie types — Q-SKY-SANGHA-FREEBIE-DELTA-01) |

### §8.5 Sangha brand catalog volume

Default volume tier per Sangha brand: **800 baseline** (matches Path X canonical brand volume per `MUSIC-MODE-BRAND-INTEGRATION-V1-01` Q3 default + `feedback_validation_before_scaling` discipline). Override via Q-SKY-SANGHA-VOLUME-TIER-01.

### §8.6 Path X frozen

The Path X 37-brand canon (`config/manga/canonical_brand_list.yaml`) is **read-only** for this program. Sangha brands do not touch it. Same pattern as `MUSIC-MODE-BRAND-INTEGRATION-V1-01` which placed music-mode brands at id 38+.

Sangha brand ID space proposal: **Sangha brands start at id 200+** (well clear of Path X 37 + music-mode 38+ + any near-term archetype additions). Confirm via Q-SKY-SANGHA-BRAND-ID-SPACE-01.

---

## §9. Onboarding flow — a new sangha member opting into karma yoga

Five stages. The first three are warm; the next two are commitment.

### §9.1 Discovery

How a sangha member hears about the program. Channels:
- A current Karma Yogi mentions it in conversation
- A Dharma Steward at a sangha event names the program
- The brochure deck (file C) is shared at quarterly satsang
- Operator names it directly at a teaching

### §9.2 Discernment

How a sangha member self-identifies which pillar fits. Discovery resources offered:
- The 7-pillar overview slide from the deck
- 1:1 conversation with current Karma Yogi or Dharma Steward (offered, not required)
- Optional skill / interest matching form (one page; lightweight)

### §9.3 First Sunday — warm-welcome protocol

When a new sangha member opts in, the matched pillar's Dharma Steward:
- Greets them by name in the opening dharma reflection
- Introduces them to one current Karma Yogi in the pillar (the "first friend")
- Walks them through one shipped deliverable so they see what "shipped" looks like

### §9.4 30-day check-in

Dharma Steward 1:1 with the new Karma Yogi:
- What is your felt experience so far?
- Is this pillar a fit, or would another pillar be a better match?
- What support do you need?

### §9.5 90-day milestone

90 days of sustained service makes a Karma Yogi eligible for their **first Pearl empowerment**. Format per Q-SKY-PEARL-EMPOWERMENT-CADENCE-01:
- Default = invited to next quarterly group empowerment ceremony from Ahjan
- 90-day individual milestone ceremony reserved for Karma Yogis completing first quarter active

The 90-day milestone is also when the Karma Yogi becomes eligible for Sangha Author consideration (P6 only) and for full Tier II access.

---

## §10. Departure / pause protocol

Volunteers may step out — with grace, not stigma. Sustained service over years is a high asking; the program holds space for life seasons.

### §10.1 Pause

A Karma Yogi who needs to pause:
- Notifies their Dharma Steward 30 days ahead when possible
- Is welcomed to return at any time without re-onboarding (within 12 months; longer absence → standard onboarding flow)
- Retains Tier II spiritual access for the remainder of the current quarter
- Tier I profit-share allocations are prorated to active quarters only

### §10.2 Departure

A Karma Yogi who steps out permanently:
- Conversation with Dharma Steward + (if desired) operator
- Dignified send-off in the next Sunday closing dedication
- Sustained-service titles retained on the lineage record (Sangha Author credit etc.)
- Tier II spiritual access for the remainder of the current quarter; not extended

**Anti-drift:** No public stigma, no "leaving the sangha" framing. Karma Yoga participation is one expression of sangha membership, not a precondition.

---

## §11. Governance + accountability

### §11.1 Who decides pillar leads

- **Initial 7 Dharma Stewards** — operator nominates post-spec-merge per Q-SKY-PILLAR-LEAD-INITIAL-01
- **Subsequent Dharma Stewards** — nomination by current Dharma Stewards (consensus) + operator confirmation
- **Rotation cadence** — annual review at the USLF retreat; rotation NOT mandatory but encouraged if a Dharma Steward has served > 2 years

### §11.2 How disputes resolve

- Pillar-internal disputes: Dharma Steward → operator
- Cross-pillar disputes: Cross-pillar Coordinator → operator
- Profit-share allocation disputes: 3-Dharma-Steward review panel + operator confirmation; legal counsel consulted if structural questions surface
- A Karma Yogi who feels the program is misframing them: 1:1 with operator. Always available.

### §11.3 Operator decision flow

Decisions categorized by envelope:
- **In-envelope** (per `docs/PEARL_OPERATOR_PROXY_SPEC.md`): Pearl_Operator_Proxy can route per existing operator decisions; logged to `artifacts/coordination/operator_decisions_log.tsv`
- **Out-of-envelope**: escalated to operator directly

This program's launch + first-year operation is **out-of-envelope by default** — operator-attended. Specific in-envelope routings to be added by operator over time as the program matures.

---

## §12. Cross-references to existing cap entries / subsystems

| Existing cap entry / subsystem | Relationship to Sangha Karma Yoga |
|---|---|
| `MUSIC-MODE-BRAND-INTEGRATION-V1-01` | Pattern precedent for first-class archetype + brands 38+; Sangha brands 200+ follow same pattern |
| `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` | Umbrella program; Sangha brand lanes (P6) land inside its catalog go-live |
| `PEARL-PRIME-STOREFRONT-V1-01` (AMENDMENT-2026-06-04) | Sangha brand storefront destination + locale parity |
| `BR-CANON-02` | Path X 37 + music 38+ + Sangha 200+ — three legitimate canons on different axes |
| `JOSHIN-SHINGON-KENJIN-ZEN` migration (OPD-105) | Joshin = Shingon lineage holder; this spec preserves the migration's framing |
| Subsystem `brand_admin` | P6 Sangha brand administrators consume brand-admin tooling |
| Subsystem `pearl_prime` | P1 Pearl Prime contributors consume pearl_prime authoring surfaces |
| Subsystem `pearl_news` | P3 Pearl News contributors consume pearl_news authoring surfaces |
| Subsystem `marketing` | P2 + P7 cross-link |
| **Subsystem `sangha_program` (NEW)** | This spec creates it |

---

## §13. Open Operator Questions (Q-SKY-* — operator answers in this section; do NOT decide on operator's behalf)

> **BATCH RATIFICATION 2026-06-11 (operator green-light; OPD-20260611-056):** All open Q-SKY-* below are RESOLVED to their stated recommended defaults, EXCEPT **`Q-SKY-LEGAL-01` = DEFERRED** (OPD-20260611-057 — profit-share legal vehicle requires legal counsel; the operator-locked 1%-per-active-contributor mechanism stands as a placeholder; no allocation is paid until counsel confirms the distribution vehicle). The six questions already operator-resolved on 2026-06-09 (MASTER-NAMING-01, MASTER-ROTATION-01, UNSAY-NAMING-01, PEARL-EMPOWERMENT-DEFINITION-01, PROFIT-PEARL-NEWS-01, 48-SOCIAL-BINDING-01) keep their inline resolutions. Each question's recommended default below is now the ratified answer of record; follow-up sub-questions (e.g. MASTER-NAMING-01b public name pick, UNSAY-SCOPE-01 cadence) remain operator-discretion at delivery.

Recommended defaults are listed inline; operator confirms or overrides.

### Q-SKY-LEGAL-01 — Profit-share LEGAL VEHICLE (narrowed by operator 2026-06-09; **DEFERRED 2026-06-11** — OPD-20260611-057)
**Status: DEFERRED** — legal counsel required for the distribution vehicle. The operator-locked mechanism (below) STANDS as placeholder; no allocation is paid until counsel confirms the vehicle. This is the ONE exception to the 2026-06-11 batch-default ratification (OPD-20260611-056).
**Operator-ratified mechanism (resolved):** 1% of Pearl Prime income per active Karma Yogi per quarter (Pearl Prime receives 5% of all-brand income; karma yogis get 1% of that). Any pillar qualifies. See §7.1.
**Remaining question:** What is the legal vehicle (LLC profit-distribution, member-association allocation, nonprofit grant pool, contractor comp arrangement, hybrid)?
**Recommended default:** Defer to legal counsel before any allocation is paid. Mechanism is locked; vehicle is the only remaining pending item.
**Blocker?** Tier I activation only. Spec ratification proceeds.

### Q-SKY-MASTER-NAMING-01 — RESOLVED (operator 2026-06-09)
Canonical = `master_feung`. Public spoken name = "Master Fan Zhou" (operator's preferred). All three names ("Master Fan Zhou" prompt-instruction / "Master Fun" LA transcript / `master_feung` repo slug) point to the same person.

### Q-SKY-MASTER-ROTATION-01 — RESOLVED (operator 2026-06-09 for Plan A)
Q1 = master_feung; Q2 = master_wu; Q3 = junko; Q4 = joshin_sensei + Ahjan Pearl Transmission. See §6 table.

### Q-SKY-UNSAY-NAMING-01 — RESOLVED (operator 2026-06-09)
UNSAY is confirmed real org. Preserve operator naming as given. Scope authority doc TBD as follow-up cap.

### Q-SKY-PEARL-EMPOWERMENT-DEFINITION-01 — RESOLVED (operator 2026-06-09)
Spec records Pearl empowerment operatively; theological definition defers to operator's own teaching at delivery.

### Q-SKY-PROFIT-PEARL-NEWS-01 — RESOLVED (operator 2026-06-09 by inclusion)
Pearl News (P3) is included in Tier I under the universal-pillar mechanism. No follow-up cap needed.

### Q-SKY-48-SOCIAL-BINDING-01 — RESOLVED (operator 2026-06-09 by universal-mechanism)
Profit-share binding is by active sangha-karma-yoga status (any pillar), not by per-pillar revenue attribution. Resolves the binding question by eliminating the pillar-specific binding requirement.

### Q-SKY-PROFIT-LAYERS-01 — Two-flow profit-share layering
**Question:** Operator's LA transcript framing names a "10% to teachers" flow for brand directors. This program's Tier I adds "1% per active contributor" for sangha karma yogis. These are two separate layers, correct?
**Recommended default:** YES — two separate layers. 10%-to-teachers (book-economics flow, pre-existing per `old_chat_specs/USLF_3_LA.txt`) + 1%-per-active-contributor (sangha-volunteer flow, new). Both apply.

### Q-SKY-PROFIT-PCT-01 — "Active" definition for profit-share
**Question:** What defines an "active contributor" for the 1% quarterly allocation?
**Recommended default:** 4+ Sundays attended in the quarter + ≥ 1 shipped deliverable per pillar.

### Q-SKY-PROFIT-CAP-01 — Total profit-share cap per project
**Question:** Total cap on profit-share pool per project per quarter (sum of all contributor %'s)?
**Recommended default:** 20% per project, distributed by contribution-weight if more than 20 contributors active.

### Q-SKY-PROFIT-PEARL-NEWS-01 — Pearl News Tier I inclusion
**Question:** Pearl News (Pillar P3) — Tier I profit-share, or Tier II spiritual-access only in V1?
**Recommended default:** Tier II only in V1; defer Tier I inclusion to follow-up cap once Pearl News revenue model matures.

### Q-SKY-PILLAR-COUNT-01 — 7 pillars correct?
**Question:** 7 pillars as listed (P1 Pearl Prime / P2 48 Social / P3 Pearl News / P4 USLF / P5 UNSAY / P6 Sangha brand administrators / P7 Sangha onboarding) — correct?
**Recommended default:** As listed. No consolidation; no expansion in V1.

### Q-SKY-PILLAR-ADD-01 — 8th pillar candidate?
**Question:** Audit surfaced no strong-fit candidate for an 8th pillar. Operator confirms 7-only for V1, or names a candidate?
**Recommended default:** None for V1. Future candidates (e.g., Pearl_Star compute stewardship if Sangha members run inference nodes; podcast pillar; video pillar) surface as separate operator decisions.

### Q-SKY-MASTER-NAMING-01 — "Master Fan Zhou" naming reconciliation
**Question:** Operator's prompt instructions name "Master Fan Zhou". Repo canonical = `master_feung` (`SOURCE_OF_TRUTH/teacher_banks/master_feung/`). Operator's LA transcript voice says "Master Fun" (Xi'an Taoist master). Same person?
**Recommended default:** Same person. Use canonical `master_feung` slug in repo references; brochure deck can use operator-preferred public name (operator chooses: "Master Fan Zhou" / "Master Fun" / "Master Feung" — Q-SKY-MASTER-NAMING-01b).

### Q-SKY-UNSAY-NAMING-01 — UNSAY naming + acronym
**Question:** "United Nations Spiritual Alliance for Youth" — is this the operator-given naming? UN-affiliated formally, or aspirational naming?
**Recommended default:** Preserve operator naming as given. Naming-vs-formal-UN-affiliation clarified in a follow-up operator decision.

### Q-SKY-UNSAY-SCOPE-01 — UNSAY pillar scope
**Question:** UNSAY pillar — youth-outreach extension of USLF? Distinct program? Operating cadence?
**Recommended default:** Youth-outreach extension of USLF for V1; cadence TBD. Operator confirms scope before P5 Dharma Steward is nominated.

### Q-SKY-MASTER-ROTATION-01 — Quarterly master teaching rotation
**Question:** Quarterly master teaching — fixed rotation (Joshin Q1 / master_feung Q2 / master_wu Q3 / Ahjan Q4)? Operator picks per quarter based on master availability? Other pattern?
**Recommended default:** Per-quarter operator pick. Spec lists the master pool, not a fixed rotation. Masters confirmed available: Joshin, master_feung, master_wu, master_sha, sai_ma (via Dayananda Das), Ahjan.

### Q-SKY-PEARL-EMPOWERMENT-CADENCE-01 — Pearl empowerment cadence
**Question:** Pearl empowerments — 1 quarterly group ceremony for all active Karma Yogis (4/year)? Plus per-90-day-milestone individual empowerment for those completing first quarter active?
**Recommended default:** Both. Quarterly group ceremony + individual 90-day milestone for first-quarter completers.

### Q-SKY-PEARL-EMPOWERMENT-DEFINITION-01 — Pearl empowerment definition
**Question:** Operator wants a written definition of what a Pearl empowerment IS for the spec, or defer the definition to operator's own teaching at delivery?
**Recommended default:** Defer the theological definition to operator's teaching at delivery. Spec records it operatively as "energy transmission from Ahjan, recognized as a unique offering only Ahjan can give." Pearl empowerments and Pearl transmissions are distinct? — sub-question, operator clarifies.

### Q-SKY-USLF-ACTIVE-DEF-01 — "Active" for USLF retreat
**Question:** USLF retreat invitation — what is "active" threshold (= invited to the annual retreat)?
**Recommended default:** 3 of 4 quarters active in the prior year.

### Q-SKY-SUNDAY-LEN-01 — Sunday Zoom length
**Question:** 60 / 45 / 90 minutes?
**Recommended default:** 60 minutes.

### Q-SKY-SUNDAY-TIME-01 — Sunday Zoom time slot
**Question:** Time slot — 9–10am PT (5pm UTC) Sundays? Global rotation across timezones?
**Recommended default:** 9–10am PT (5pm UTC) Sundays for V1; record for async catch-up. Global rotation considered in V2 once cohort spans multiple regions.

### Q-SKY-COHORT-CAP-01 — Phase A first-cohort headcount
**Question:** First cohort headcount cap?
**Recommended default:** 12–20 for Phase A (one quarter trial).

### Q-SKY-ARCHIVE-01 — Volunteer-only recorded archive
**Question:** Volunteer-only archive of recorded teachings + Sunday meetings — yes/no?
**Recommended default:** Yes, after explicit consent from each teacher per recording. Sunday recordings shared with active cohort same-day.

### Q-SKY-1V1-MASTER-01 — 1:1 time with masters (Tier III)
**Question:** Allow rare 1:1 time with masters for sustained-service Karma Yogis?
**Recommended default:** Yes; operator-curated, not advertised as guaranteed.

### Q-SKY-STIPEND-01 — USLF retreat travel stipend
**Question:** Travel stipend for the USLF retreat for active Karma Yogis?
**Recommended default:** Case-by-case, operator-discretion.

### Q-SKY-DEPARTURE-PROTOCOL-01 — Departure protocol
**Question:** Confirm the §10 protocol (30-day notice; Dharma Steward exit conversation; dignified Sunday closing)?
**Recommended default:** As §10 specifies.

### Q-SKY-DECK-DIRECT-ADDRESS-01 — Slide 18 operator direct-address
**Question:** Slide 18 "Words from Ahjan" — operator drafts 50–150 words pre-publish?
**Recommended default:** Skeleton placeholder this session; operator fills in pre-publish.

### Q-SKY-PILLAR-LEAD-INITIAL-01 — Initial 7 Dharma Stewards
**Question:** Who are the initial 7 Dharma Stewards (one per pillar)?
**Recommended default:** Operator nominates post-spec-merge.

### Q-SKY-48-SOCIAL-BINDING-01 — 48 Social Tier I binding
**Question:** Mechanism for binding sangha karma yogi contributors to 48 Social profit-share pool — by post-attribution? By active-pillar membership? By campaign assignment?
**Recommended default:** By active-pillar membership for V1. Per-post-attribution refinement for V2 once measurement infrastructure matures.

### Q-SKY-USLF-AUTHORITY-DOC-01 — USLF formal authority doc
**Question:** USLF currently has no formal authority doc — operator's LA transcript is the canonical source. Author one as follow-up cap?
**Recommended default:** YES — Pearl_Architect follow-up cap to author `docs/specs/USLF_V1_PROGRAM_SPEC.md` after this V1 cap merges.

### Q-SKY-WIZARD-MODE-01 — Sangha mode in brand wizard step 1
**Question:** Add Sangha mode option to brand wizard step 1 mode selector?
**Recommended default:** Yes — V1.1 follow-up cap. Not in V1 scope.

### Q-SKY-COMPOSITE-VOICE-RULES-01 — Sangha brand composite-voice rules
**Question:** How does a Sangha brand lane blend teachings from ≥ 3 master banks at the atom level — by registry weighting? By teacher rotation per book? By thematic curation per brand?
**Recommended default:** V1.1 follow-up cap. Initial Sangha brand lanes hand-curated by Sangha Author + P6 Dharma Steward.

### Q-SKY-SANGHA-COVER-TREATMENT-01 — Sangha brand cover treatment
**Question:** Sangha brand covers — composite visual language (alliance-rooted) or single-archetype?
**Recommended default:** V1.1 follow-up cap.

### Q-SKY-SANGHA-FREEBIE-DELTA-01 — Sangha freebie type deltas
**Question:** Sangha brands ride existing freebie types, or get Sangha-specific freebies (free meditations + new-student onboarding hooks)?
**Recommended default:** Ride existing freebies for V1; Sangha-specific deltas as V1.1 follow-up cap (parallel to `MUSIC-MODE-FREEBIE-FUNNEL-V1-02` pattern).

### Q-SKY-SANGHA-VOLUME-TIER-01 — Sangha brand catalog volume
**Question:** Sangha brand default catalog volume tier — 800 baseline like Path X canonical brand?
**Recommended default:** 800 baseline. Override via per-Sangha-brand wizard field once V1.1 brand-wizard work lands.

### Q-SKY-SANGHA-BRAND-ID-SPACE-01 — Sangha brand ID space
**Question:** Sangha brands start at id 200+ (clear of Path X 37 + music 38+)?
**Recommended default:** 200+.

---

## §14. LLM Tier Policy compliance + repo constraints inherited

Per `CLAUDE.md`:

- **This session = Tier 1** (operator-present, design + ratification work)
- **No paid LLM APIs** invoked in this session or projected for the program
- **No repo-code changes** in this PR (program-design only)
- **Pearl Star / Qwen / Gemma** (Tier 2) acceptable for unattended pipeline runs *after* this spec ratifies + downstream workstreams open
- **`scripts/ci/audit_llm_callers.py`** policy applies to any future code that touches LLM clients
- **Sunday meetings**, master teachings, Pearl empowerments — all human-facilitated, no LLM exposure

---

## §15. Phased rollout

### Phase A — Pilot cohort (one quarter)
- Invite first 12–20 sangha members per Q-SKY-COHORT-CAP-01
- Operator nominates initial 7 Dharma Stewards per Q-SKY-PILLAR-LEAD-INITIAL-01
- Run one full quarter (12 Sundays + 1 master teaching + 1 Pearl empowerment)
- Collect Karma Yogi feedback in 30-day + 60-day + 90-day check-ins
- Tier I (profit-share) is **placeholder during Phase A** — legal-counsel review concludes before any actual allocation
- Operator-attended throughout

### Phase B — Full sangha cohort
- Expand to full sangha
- Open second Sunday cohort if demand justifies (Q-SKY-SECOND-SUNDAY-COHORT-01)
- Phase A cohort becomes Wave 1; Phase B becomes Wave 2 — both meet the same Sunday rhythm, separate cohorts if needed
- Tier I profit-share **activates** once legal-counsel review concludes per Q-SKY-LEGAL-01

### Phase C — Formalization
- Legal profit-share structure formalized
- Authority doc for USLF authored (Q-SKY-USLF-AUTHORITY-DOC-01)
- V1.1 follow-up caps for Sangha brand wizard mode, composite voice rules, Sangha freebie deltas, Sangha cover treatment land
- Annual USLF retreat establishes recurring rhythm

### Phase D — Steady state
- Program operates on the quarterly cadence + annual USLF retreat
- Cross-pillar Coordinator rotation pattern established
- Sangha Author lineage records established
- Pearl Empowered population grows organically through 90-day milestones + quarterly group ceremonies

---

## §16. Anti-drift

1. **No invented spiritual benefits.** Pearl empowerments + master teachings are gifts, not contractual entitlements. Frame language stays humble.
2. **No marketing-funnel voice on the brochure deck.** Sangha-to-sangha voice only. The reader already knows karma yoga.
3. **No specific dollar amounts on profit-share.** Mechanism + framework only; legal counsel determines actual numbers.
4. **No 8th work pillar without operator approval.** Surface as Q-SKY-PILLAR-ADD-01.
5. **No paid LLM APIs** per `CLAUDE.md` Tier policy.
6. **No code changes** in this PR. Program-design only.
7. **No Path X 37 touch.** Sangha brand ID space starts at 200+.
8. **No edits to Pearl Prime / 48 Social / Pearl News code or config** in this PR.
9. **No silent decision-making on Q-SKY-* items.** Recommend defaults; operator decides.
10. **Operator-given naming preserved** (UNSAY, Master Fan Zhou, Pearl empowerment) even when canonical repo slug differs (`master_feung` etc.). Reconciliation flagged via Q-SKY-MASTER-NAMING-01.

---

## §18. Level Progression Layer — V1.5 amendment (cross-link)

This V1 spec defines program structure (pillars + rhythm + reward tiers + onboarding). The **per-quarter level progression layer** — what each of the 4 quarterly empowerments names and confers, the per-level Pearl News feedback loop, the 4 alternative spiritual paths (Plan A / B / C / D) the operator can choose from at Phase A launch — lives in the V1.5 amendment:

→ **`docs/specs/SANGHA_KARMA_YOGA_LEVEL_PROGRESSION_SPEC.md`**

That spec defines:
- The 1-year arc skeleton (4 quarters × 4 empowerments × 4 attainment levels)
- **Plan A — Vairocana World Bodhisattva ladder** (operator's own progression — master rotation in §6 of this spec maps onto Plan A's per-level domains)
- **Plan B — Mahāyāna Six Paramita compressed ladder** (alternative)
- **Plan C — Vajrayāna 4-Initiation inspired ladder** (alternative; "inspired by" framing, not actual abhiṣeka transmission)
- **Plan D — Tao-Buddha-Hindu-Pearl Polestar ladder** (alternative; one tradition per quarter)
- Comparison matrix
- Pearl News feedback-loop integration spec (monthly Volunteer Digest; per-level world-good-news domain)
- Per-quarter ceremony + ritual shape
- 12+ Q-OP-* operator decision items
- Cap entry `SANGHA-KARMA-YOGA-V1-01-AMENDMENT-2026-06-06-LEVELS`

The V1.5 layer slots into V1 cleanly — V1 holds the program *body*; V1.5 holds the *year-of-becoming arc*. Both layers ratify together in this PR; Plan selection (A vs B vs C vs D vs parallel-tracks) is the operator's Q-OP-PROGRESSION-SHIP-01 decision in the V1.5 §11 decision card.

---

## §17. Pointers

- `docs/PEARL_ARCHITECT_STATE.md` (cap entry `SANGHA-KARMA-YOGA-V1-01`)
- `artifacts/coordination/ACTIVE_PROJECTS.tsv` (row `PRJ-SANGHA-KARMA-YOGA-V1`)
- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv` (row `sangha_program`)
- `artifacts/programs/sangha_karma_yoga_20260606/SANGHA_KARMA_YOGA_OVERVIEW.md` (long-form prose companion)
- `artifacts/programs/sangha_karma_yoga_20260606/SANGHA_KARMA_YOGA_INVITATION.pptx` (operator-facing brochure deck)
- `old_chat_specs/USLF_3_LA.txt` (operator's canonical USLF source)
- `./teachers/ahjan/intake/Dharma Talks/` (23 Sangha-related operator dharma talks 2018–2022)

---

**End of spec.**
