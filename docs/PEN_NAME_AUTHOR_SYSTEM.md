# Pen-Name Author & Teacher Profile System

**Authority**: This document is the single source of truth for the multi-author pen-name system, EU skeleton brands, and teacher-mode writer profiles.
**Last updated**: 2026-03-24
**System**: Phoenix V4 Multi-Brand Audiobook Pipeline

---

## 1. System Overview

The pen-name author system creates locale-appropriate fictional authors for each brand lane, giving the pipeline the ability to generate thousands of unique audiobooks per brand without triggering platform anti-spam filters. Each author has a permanently locked voice, a positioning profile, topic/persona scores, scenario seeds, and hook atoms — enough to generate 1,000+ books per author.

### Scale

| Metric | Count |
|--------|-------|
| Total author slots (brand pools) | 480 |
| Unique authors / teacher IDs | 452 |
| Total brands covered | 72 production + 3 special |
| Total locales | 13 |
| Authors per EN brand | 8 |
| Authors per non-EN brand | 6 |
| Teacher profile rows (full JSON) | 480 |
| Teacher profiles (unique YAML registry) | 452 |
| Scenario seeds | 7,113 |
| Hook atoms | 3,506 |
| Topics scored per teacher | 15 (all canonical) |
| Theoretical book capacity | 155,000+ |

### Locale Distribution

| Locale | Brands | Authors | Phase |
|--------|--------|---------|-------|
| en-US | 24 | 192 | Phase 1 (active) |
| zh-TW | 6 | 36 | Phase 1 (active) |
| zh-HK | 6 | 36 | Phase 2-3 (Mo 6-9) |
| zh-CN | 6 | 36 | Phase 5 (Mo 10-18) |
| zh-SG | 6 | 36 | Phase 5 (Mo 12-18) |
| ja-JP | 6 | 36 | Phase 2 (Mo 4-6) |
| ko-KR | 4 | 24 | Phase 3 (Mo 5-7) |
| de-DE | 3 | 18 | Phase 4 (Mo 7-12) |
| fr-FR | 2 | 12 | Phase 4 (Mo 7-12) |
| it-IT | 2 | 12 | Phase 4 (Mo 7-12) |
| hu-HU | 2 | 12 | Phase 4 (Mo 7-12) |
| es-US | 3 | 18 | Phase 4 (Mo 7-12) |
| es-ES | 2 | 12 | Phase 4 (Mo 7-12) |

---

## 2. Architecture

```
brand_archetype_registry.yaml (24 EN archetypes)
        │
        ├── brand_registry.yaml (51 non-archetype brands: ZH/JA/KO/EU + special)
        │
        ├── brand_registry_locale_extension.yaml (locale fields per brand)
        │
        ├── brand_author_assignments.yaml ──── 480 author slots (8/EN, 6/non-EN)
        │       │
        │       └── Each author → voice_lock (ElevenLabs voice ID), tier
        │
        ├── brand_narrator_assignments.yaml ── 75 brands → default narrator + voice_id
        │
        ├── voice_author_lock_table.yaml ───── 389 permanent voice-to-author locks
        │
        ├── author_positioning_profiles.yaml ─ 3 profile types: somatic_companion,
        │                                       research_guide, elder_stabilizer
        │
        ├── pen_name_teacher_profiles.yaml ─── 452 unique teacher profiles (YAML, core fields)
        │       │
        │       ├── ei_profile (locale-language tradition phrase, methodology)
        │       ├── topic_scores (all 15 canonical topics, 0.0-1.0)
        │       ├── persona_scores (locale personas, 0.0-1.0)
        │       └── voice_signature (tone, metaphors, forbidden markers)
        │
        ├── pen_name_teacher_profiles_full.json ── 480 profile rows + scenario_seeds + hook_atoms
        │
        ├── author_pic_prompts.yaml ──────── 10 portrait presets, 393 author mappings
        │
        └── author_cover_art_registry.yaml ── Cover art base + palette tokens per author
```

---

## 3. Config File Reference

### 3.1 brand_author_assignments.yaml

**Path**: `config/brand_author_assignments.yaml`
**Purpose**: Multi-author pen-name pools per brand. Pipeline resolves author from this file.
**Structure**: 75 brand entries, each with `default_author` and `author_pool` (list of `{author_id, voice_lock, tier}`).
**Anti-spam**: 8 authors per EN brand, 6 per ZH/JA/KO/EU brand. No voice appears more than twice per brand within a locale.

### 3.2 brand_narrator_assignments.yaml

**Path**: `config/brand_narrator_assignments.yaml`
**Purpose**: Default narrator and voice_id per brand (75 entries). Sections: EN, ZH-TW, ZH-HK, ZH-CN, ZH-SG, JA-JP, KO-KR, Special, EU.

### 3.3 voice_author_lock_table.yaml

**Path**: `config/voice_author_lock_table.yaml`
**Purpose**: 389 permanent voice-to-author locks. Once assigned, a voice is permanently bound to an author.
**Warning**: ElevenLabs default voices expire 2026-12-31. Migration planning needed.

### 3.4 pen_name_teacher_profiles.yaml

**Path**: `config/authoring/pen_name_teacher_profiles.yaml` (793 KB)
**Purpose**: Master YAML registry of 452 unique teacher profiles. Pipeline-readable. Contains core fields only (no scenarios/hooks — those are in the JSON).
**Fields per teacher**: teacher_id, display_name, brand_id, locale, positioning_profile, ei_profile, topic_scores (15), persona_scores, voice_signature.

### 3.5 pen_name_teacher_profiles_full.json

**Path**: `config/authoring/pen_name_teacher_profiles_full.json` (1.8 MB)
**Purpose**: Complete JSON export with scenario_seeds and hook_atoms. Use this for book generation.
The current recovered export contains 480 profile rows covering 452 unique teacher IDs because some locale teachers are intentionally reused across related brand lanes.
**Fields per teacher**: All YAML fields + scenario_seeds (dict of topic → list of scenarios), hook_atoms (dict of topic → list of hooks).

### 3.6 author_pic_prompts.yaml

**Path**: `config/authoring/author_pic_prompts.yaml`
**Purpose**: 10 portrait style presets with prompt engineering for AI-generated author photos. 393 author-to-preset mappings.
**Presets**: contemplative, grounded, radiant, authority, energetic, scientific, warm_intimate, stoic_minimal, youthful_peer, legacy_wisdom.

### 3.7 author_cover_art_registry.yaml

**Path**: `config/authoring/author_cover_art_registry.yaml`
**Purpose**: Cover art base images and palette tokens per author. Asset path pattern: `assets/authors/cover_art/{author_id}_base.png`.

### 3.8 brand_registry.yaml

**Path**: `config/brand_registry.yaml`
**Purpose**: Master brand lifecycle registry. 51 brands (24 ZH variants + 6 JA + 4 KO + 14 EU + 3 special). EN canonical brands live in `brand_archetype_registry.yaml`.

---

## 4. EU Skeleton Brands (Phase 4)

14 brands created for 6 EU locales, following the NEW_LANGUAGE_LOCATION_ONBOARDING.md framework.

| Locale | Brand ID | Display Name | Archetype Base |
|--------|----------|-------------|----------------|
| de-DE | sleep_repair_de | Schlaf-Reparatur | night_reset |
| de-DE | stabilizer_de | Stabilisator | stabilizer |
| de-DE | adhd_anchor_de | ADHS-Anker | adhd_forge |
| fr-FR | sleep_repair_fr | Réparation du Sommeil | night_reset |
| fr-FR | stabilizer_fr | Stabilisateur | stabilizer |
| it-IT | sleep_repair_it | Riparazione del Sonno | night_reset |
| it-IT | stabilizer_it | Stabilizzatore | stabilizer |
| hu-HU | stabilizer_hu | Stabilizátor | stabilizer |
| hu-HU | sleep_repair_hu | Alvás-helyreállítás | night_reset |
| es-US | sleep_repair_es_us | Reparación del Sueño | night_reset |
| es-US | stabilizer_es_us | Estabilizador | stabilizer |
| es-US | burnout_recovery_es_us | Recuperación del Agotamiento | stabilizer |
| es-ES | sleep_repair_es_es | Reparación del Sueño | night_reset |
| es-ES | stabilizer_es_es | Estabilizador | stabilizer |

**EU voice IDs**: Placeholder format (`de_voice_01`, `fr_voice_01`, etc.) pending ElevenLabs voice audition for each locale.

---

## 5. Positioning Profiles

Three author positioning profiles govern trust posture, language, and vulnerability:

| Profile | Authority Type | Trust Anchor | Vulnerability |
|---------|---------------|-------------|---------------|
| somatic_companion | lived_experience | companion | moderate |
| research_guide | research_synthesizer | analyst | low |
| elder_stabilizer | seasoned_practitioner | elder | low |

---

## 6. Topic Score System

All 452 unique teacher profiles have scores (0.0-1.0) for all 15 canonical topics:

anxiety, boundaries, burnout, compassion_fatigue, courage, depression, financial_anxiety, financial_stress, grief, imposter_syndrome, overthinking, self_worth, sleep_anxiety, social_anxiety, somatic_healing.

**Score bands**: strong (0.7-1.0, full allocation), medium (0.4-0.7, normal allocation), weak (0.0-0.4, fewer books, prefer shorter formats).

Brand-primary topics score 0.8-0.95. Secondary topics 0.6-0.75. Others 0.4-0.55.

---

## 7. Voice Tier System

EN brands use an 80/20 tier system: Tier-1 (12 voices, 80% of book output), Tier-2 (19 voices, 20% rotation). Non-EN locales use rotation across their smaller voice pools.

---

## 8. Deliverable Spreadsheets

| File | Sheets | Purpose |
|------|--------|---------|
| `author_bios_global_complete.xlsx` | 16 (Summary + 13 locale + Brand Coverage + EU Brands) | Author bios tied to brand personas and topics |
| `teacher_profiles_global_complete.xlsx` | 17 (Summary + 13 locale + Scenarios + Hooks + Topic Scores) | Full teacher profiles with scenario library |
| `brand_lane_catalog_global_complete.xlsx` | 8 (Locale Strategy + locale author sheets + EU + Voice + Summary) | Brand-lane catalog and planning |

---

## 9. Verification

Run verification:

```bash
python3 scripts/verify_pen_name_coverage.py
```

Expected output:
- 480 author-pool slots across 75 known brands
- 452 unique teacher profiles with 15/15 topic scores each
- 480 full JSON profile rows
- 7,113 scenario seeds
- 3,506 hook atoms
- 0 gaps in topic scores, persona scores, scenarios, or hooks

---

## 10. Related Docs

- [LOCALE_PERSONAS.md](./LOCALE_PERSONAS.md) — 46 personas across 12 locales
- [NEW_LANGUAGE_LOCATION_ONBOARDING.md](./NEW_LANGUAGE_LOCATION_ONBOARDING.md) — Onboarding framework for new locales
- [AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md](./AUDIOBOOK_LOCALE_CATALOG_MARKETING_PLAN.md) — Phased rollout and locale strategy
- `config/catalog_planning/brand_archetype_registry.yaml` — 24 EN brand archetypes
- `config/localization/brand_registry_locale_extension.yaml` — Locale brand definitions
- `config/marketing/platform_antispam_rules.yaml` — Platform anti-spam rules
- `config/marketing/consumer_language_by_topic.yaml` — Consumer language per topic per locale
