# V1.2 themes — en_US — Cluster E (Gen-Alpha/School/Identity) summary

**Deliverable:** `artifacts/marketing/v1_2_themes_en_US_cluster_e.yaml`
**Schema:** V1.2 (strict enum compliance).
**Total series:** 25 (5 brands × 5 series).
**Cluster:** E — Gen-Alpha/School/Identity.

## Brand-id mapping (constraint doc → canonical_brand_list.yaml)

| Constraint doc (Cluster E candidate) | Mapped canonical brand_id     | Rationale                                                                                                |
| ------------------------------------ | ----------------------------- | -------------------------------------------------------------------------------------------------------- |
| `digital_ground`                     | `digital_ground`              | EXACT — flagship manhwa, burnout / tech worker / digital identity.                                       |
| `gen_z_grounding`                    | `calm_student_school`         | MAPPED — closest Gen Alpha school/grounding canonical (anxiety/study/shojo). "Calm student" = grounding. |
| `confidence_core`                    | `confidence_core_romance`     | EXACT ROOT — shojo imposter syndrome / self-worth / identity, with romance framing.                      |
| `mecha_identity`                     | `solar_return_isekai`         | MAPPED — shonen self-worth/imposter framed as isekai. Closest portal-identity canonical for mech jumps.  |
| `queer_identity_growth`              | `creative_unfold_social`      | MAPPED — shojo social-anxiety/creativity/courage. Closest queer-creative identity register canonical.    |

## Distributions (validated against V1.2 strict enums)

### Genre family (target vs delivered)

| Genre                  | Target  | Delivered | Status |
| ---------------------- | ------- | --------- | ------ |
| healing                | 6       | 6         | ✓      |
| slice_of_life          | 5       | 5         | ✓      |
| supernatural_everyday  | 4       | 4         | ✓      |
| mystery_cozy           | 4       | 4         | ✓      |
| fantasy_adventure      | 2       | 2         | ✓      |
| romance                | 2       | 2         | ✓      |
| school                 | 2 (2–3) | 2         | ✓ (Cluster E bumps school to ceiling) |
| **TOTAL**              | 25      | 25        | ✓      |

All `genre_family` values are within the strict V1.2 canonical enum.

### Magical register

| Register              | Count |
| --------------------- | ----- |
| none                  | 14    |
| supernatural_everyday | 7     |
| magical_realism       | 2     |
| isekai                | 2     |

All values within the strict V1.2 enum (`supernatural_everyday / magical_realism / soft_fantasy / isekai / occult_cosmic / none`). NO `high_fantasy` (banned).

### Serial engine

| Engine                   | Count |
| ------------------------ | ----- |
| case_of_the_week         | 9     |
| companion_roster         | 6     |
| mystery_box              | 4     |
| life_stage_rhythm        | 4     |
| power_escalation_ladder  | 2     |

All values within the strict V1.2 enum. NO `location_anthology` used (acceptable — enum-valid).

## Persona distribution (Gen Alpha lean)

| Bucket                   | Count | %       |
| ------------------------ | ----- | ------- |
| GA-quiet (Gen Alpha)     | 10    | 40%     |
| GA-streamer (Gen Alpha)  | 8     | 32%     |
| GA-coder (Gen Alpha)     | 3     | 12%     |
| GA-queer (Gen Alpha)     | 1     | 4%      |
| GZ-uni (Gen Z)           | 3     | 12%     |
| **Gen Alpha total**      | **22**| **88%** |
| **Gen Z total**          | **3** | **12%** |

Gen Alpha allocation **88%** — exceeds the 35% floor and the 35–50% target by design. Cluster E is the **heaviest Gen Alpha cluster**, as specified.

## Runway

- Median: **175** volumes.
- Mean: **170.4** volumes.
- Range: 150–200.

## Voice register

My Hero Academia / Spy x Family / Heartstopper / Komi Can't Communicate. Earnest, identity-affirming, specific. Avoids TikTok-cringe register, performative wokeness, overly explained therapy. Gen Alpha treated as AI-native (AI companions, mascots, app-portals, character-jumps are ordinary furniture of adolescence, not novelty).

## Authority chain

- BINDING per-cluster allocation: `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`
- Magical/serial framework: `artifacts/research/manga_bestseller_magical_serial_framework_2026-05-12.md` (PR #1051)
- Gen Z / Gen Alpha portals: `artifacts/research/manga_genz_genalpha_portal_framework_2026-05-13.md` (PR #1053)
- 37-brand canon: `config/manga/canonical_brand_list.yaml`

## File list (write_scope ≤ 4, this PR uses 2)

1. `artifacts/marketing/v1_2_themes_en_US_cluster_e.yaml` (deliverable, 25 series, 5 brands)
2. `artifacts/marketing/v1_2_themes_en_US_cluster_e_summary.md` (this file)

Zero deletions. Zero LLM-API callers introduced. Other cluster files untouched.
