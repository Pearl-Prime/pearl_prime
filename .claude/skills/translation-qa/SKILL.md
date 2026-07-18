# Translation QA Skill

Use this skill for Phoenix Omega atom localization, locale repair, and
translation-closeout review.

## Core Contract

Phoenix atom localization is complete only when every target locale file has
the same usable atom header set as its English source, with localized body text
that passes locale/script expectations.

Do not treat file existence, header count, or catalog percentage alone as proof
of translation quality.

## Required Checks

1. Compare each localized `CANONICAL.txt` to the English source file.
2. Header IDs must match exactly, including slot/family and version number.
3. No duplicate localized header IDs.
4. No missing localized header IDs.
5. No extra localized header IDs unless the repo has an explicit migration rule.
6. Body text must not be empty, placeholder-only, TODO-only, or English fallback.
7. Preserve variables, markdown links, HTML tags, template tokens, glossary terms,
   and brand/product names exactly unless the source explicitly localizes them.
8. Preserve clinical and safety meaning. Do not soften warnings, disclaimers,
   contraindications, or crisis language.
9. Preserve persona, topic, arc, emotional beat, and practical exercise function.
10. Do not lower production, locale, parser, or coverage gates.

## Locale Script Expectations

- `ja-JP`: natural Japanese, not Chinese text with Japanese particles added.
- `ko-KR`: natural Korean, Hangul-centered, not Japanese or Chinese fallback.
- `zh-TW`: Traditional Chinese for Taiwan, not Simplified, not Mainland wording.
- `zh-HK`: Traditional Chinese for Hong Kong, Hong Kong vocabulary where relevant.
- `zh-SG`: Simplified Chinese for Singapore, not Taiwan/Hong Kong wording.
- `zh-CN`: Simplified Chinese for Mainland China.
- `es-US`: neutral Latin American / US Spanish, not Spain Spanish.
- `es-ES`: Spain Spanish, not Latin American-only usage.
- `pt-BR`: Brazilian Portuguese, not Portugal Portuguese.
- `fr-FR`, `de-DE`, `it-IT`, `hu-HU`: native European locale, not English syntax.

## Phoenix Commands

Use the repo's live localization worklist when available:

```bash
PYTHONPATH=. python3 scripts/localization/build_14_locale_worklist.py \
  --out artifacts/qa/localization_14_coverage_$(date +%Y%m%d_%H%M%S)
```

If the script path has moved, find the authoritative coverage/worklist script
before editing. Do not invent coverage numbers.

## Closeout Format

```text
TRANSLATION_LOCALE_CLOSEOUT:
- locale:
- branch:
- source_base_sha:
- files_changed:
- missing_before:
- partial_before:
- missing_after:
- partial_after:
- validation_commands:
- remaining_true_blockers:
```

If blocked, report exactly one real blocker with the source path, localized path,
command output, and why it prevents honest completion.

