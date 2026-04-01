# Brand Admin Onboarding Wizard Spec

**Purpose:** The **BrandWizard** experience is the decision-teaching core: more than settings collection—it explains tradeoffs, shows registry-driven proof (with proof-pending fallbacks), and outputs a concise operating summary.

**Related docs:**

- [ONBOARDING_OUTPUT_PROOF_SYSTEM.md](./ONBOARDING_OUTPUT_PROOF_SYSTEM.md) — registry UX, stale-`ready`, JSON delivery.
- [ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md](./ONBOARDING_REAL_EXAMPLE_GENERATION_SPEC.md) — example matrix, `cmp_*` sets, field schema.
- [BRAND_ADMIN_MEDIA_GENERATION_SPEC.md](./BRAND_ADMIN_MEDIA_GENERATION_SPEC.md) — canonical image/video generation contract, QA gates, and registry linkage.
- [BRAND_ADMIN_ONBOARDING_IMAGE_PACK_V1_TRUST_LAYER_SPEC.md](./BRAND_ADMIN_ONBOARDING_IMAGE_PACK_V1_TRUST_LAYER_SPEC.md) — Image Pack v1 (19 prompts, rubric, wizard step placement).
- [docs/BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md](../docs/BRAND_ADMIN_ONBOARDING_PAGES_SPEC.md) — surrounding pages.
- Config: [config/onboarding/wizard_decision_explainer_data.json](../config/onboarding/wizard_decision_explainer_data.json), [config/onboarding/example_registry.json](../config/onboarding/example_registry.json).
- Implementation: [brand-wizard-app/src/BrandWizard.jsx](../brand-wizard-app/src/BrandWizard.jsx) (evolve incrementally).

---

## 1. Product principle

Every important claim should be backed by at least one of:

- registry-linked proof (`ships_product` / `teaches_comparison`),
- explainer copy from `wizard_decision_explainer_data.json`,
- revenue/workload **stubs** (until dashboard mode is wired).

The wizard output is the authoritative brand contract. Downstream media generation must remain contract-locked (no manual drift from wizard decisions), as defined in [BRAND_ADMIN_MEDIA_GENERATION_SPEC.md](./BRAND_ADMIN_MEDIA_GENERATION_SPEC.md).

---

## 2. Wizard flow (target)

### Step 1 — Mission lane

Options: self-help, audiobooks, manga, Pearl News / civic editorial, breathwork/tools, hybrid.

**Show:** lane copy, `exampleIds`, workload hint, revenue shape stub.  
**Components:** `LaneChoiceCard`, `OutputProofStrip`, sidebar summary.

### Step 2 — Market / language / locale

**Show:** market behavior, platform hints, localized `exampleIds` when `ready`.  
**Components:** `MarketChoiceCard`, `LocalizedExampleStrip`, optional mini scenario.

### Step 3 — Audience / persona

**Show:** persona visuals (`proof_intent: teaches_persona` or comparison members).  
**Components:** `PersonaVisualCard`, `AudienceFitExplainer`.

### Step 4 — Topic family

**Show:** topic visuals (`teaches_topic`), lane fit notes.  
**Components:** `TopicExperienceCard`, `TopicLaneRecommendation`.

### Step 5 — Platform strategy

**Show:** speed to launch, asset burden, `exampleIds` for packaging types.  
**Components:** `PlatformMixCard`, `AssetRequirementPanel`.

### Step 6 — Brand posture

**Show:** **comparison board** using `comparison_set_id` (e.g. `cmp_burnout_posture_v1`).  
**Components:** `ControlledComparisonBoard`, `DecisionImpactSummary`.

### Step 7 — Content / creative knobs

**Show:** side-by-side text or visual diffs when registry has pairs; else placeholders.  
**Components:** `KnobComparisonPanel`, `TextOutputDiff`, `VisualOutputDiff`.

### Step 8 — Weekly workload preview

**Show:** estimated review burden from choices.  
**Components:** `WeeklyOSPreview`, `WorkloadMeter`.

### Step 9 — Revenue scenarios

**Show:** conservative / likely / upside stubs (links to `revenue_dashboard.jsx` onboarding mode when present).  
**Components:** `ScenarioRevenueCards`, `RampTimeline`.

### Step 10 — Personalized operating plan

**Show:** recap + next actions + link to weekly OS page.  
**Components:** `OperatingPlanSummary`, `LaunchChecklist`.

---

## 3. UX rules

1. Do not show abstract knobs without copy + optional proof strip.
2. Use **`fetch('/onboarding/example_registry.json')`** (or build-time copy in `public/onboarding/`) so dev and Pages stay aligned.
3. Respect [ONBOARDING_OUTPUT_PROOF_SYSTEM.md](./ONBOARDING_OUTPUT_PROOF_SYSTEM.md) §4 for all thumbnails and heroes.

---

## 4. Engineering constraints

- **Do not** rewrite [BrandWizard.jsx](../brand-wizard-app/src/BrandWizard.jsx) in one PR. Add `brand-wizard-app/src/onboarding/*` modules and wire **one or two** steps first (`OutputProofStrip` + one lane/market screen).
- Explainer JSON is keyed by `laneConfig`, `marketConfig`, `personaConfig` (extend as needed).

---

## 5. Output artifact (future)

Persisted JSON or markdown “operating plan” export may be added later; not required for scaffold v1.
