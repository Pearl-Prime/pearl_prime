# Adi Da Teacher Bank

**Teacher ID:** `adi_da`
**Display name:** Adi Da
**Doctrine:** `doctrine/doctrine.yaml`
**Registry:** `config/teachers/teacher_registry.yaml`

## Doctrine core

- **The Bright / prior freedom:** What you are before all seeking; your fundamental nature
- **Contraction:** The fundamental holding pattern; the activity of the separate self
- **Recognition vs seeking:** Stopping the search reveals what was always here
- **Relationship as mirror:** The other reflects your own state of contraction
- **Conscious Process:** Attention to Reality, release from separate self
- **Conductivity:** Natural energy flow when contraction is not blocking

## Slot coverage (native en-US)

| Slot | Count | Status |
|------|-------|--------|
| HOOK | 24 | F006 ready |
| SCENE | 20 | F006 ready |
| STORY | 20 | F006 ready |
| REFLECTION | 24 | F006 ready |
| COMPRESSION | 20 | F006 ready |
| EXERCISE | 20 | F006 ready |
| INTEGRATION | 20 | F006 ready |
| PIVOT | 20 | Extended slot |
| TAKEAWAY | 20 | Extended slot |
| THREAD | 20 | Extended slot |
| PERMISSION | 20 | Extended slot |
| TEACHER_DOCTRINE | 8 | Band-1 doctrine overlay (doctrine_grounded) |

**TEACHER_DOCTRINE** atoms (`approved_atoms/TEACHER_DOCTRINE/`) are band-1, full-section
doctrine atoms (one per main teaching atom + a no-bypassing boundary atom), authored
`synthesis_method: doctrine_grounded` from `doctrine/doctrine.yaml` and
`doctrine/main_teaching_atoms.yaml`. They follow the same on-disk convention as the
ahjan teacher-bank doctrine atoms. The retired QUOTE slot (per QUOTE-ATOM-ROUTING-01 /
PR #915, "retire-as-orphan") is intentionally absent — teacher-voice doctrinal content
is routed to TEACHER_DOCTRINE, not a QUOTE slot.

## Localization status

### Localized (6 locales)

- ja-JP (Japanese)
- ko-KR (Korean)
- zh-CN (Simplified Chinese)
- zh-HK (Traditional Chinese, Hong Kong)
- zh-SG (Simplified Chinese, Singapore)
- zh-TW (Traditional Chinese, Taiwan)

### Intentional exclusions (6 locales)

The following locales from `locale_registry.yaml` do not yet have Adi Da localized atoms. This is an intentional deferral, not an oversight. Rationale:

- **es-US, es-ES (Spanish):** Adidam community presence is minimal in Spanish-speaking markets. Localize when catalog demand or market data justifies investment.
- **fr-FR (French):** Limited Adidam community presence in France. Defer to catalog demand.
- **de-DE (German):** Limited Adidam community presence in Germany. Defer to catalog demand.
- **it-IT (Italian):** No established Adidam community presence. Defer to catalog demand.
- **hu-HU (Hungarian):** No established Adidam community presence. Defer to catalog demand.

**To add a locale:** Translate from en-US template atoms into `approved_atoms_localized/<locale>/` following the existing ja-JP/ko-KR/zh-CN structure. Each localized atom retains the same `atom_id` with a `_<locale>` suffix.

## Copyright and sourcing policy

- All atoms use `synthesis_method: doctrine_grounded` (paraphrase + original composition)
- No verbatim passages from published Adidam works
- Official Adidam URLs may be referenced in `source_refs` for citation
- Devotional terminology adapted for non-devotional Phoenix brands where needed

## Scoring

Topic and persona fit scores are defined in `config/catalog_planning/teacher_topic_persona_scores.yaml`. Strong fits: anxiety (0.85), grief (0.85), overthinking (0.8), boundaries (0.8), self_worth (0.8). Weaker fits default to 0.5.
