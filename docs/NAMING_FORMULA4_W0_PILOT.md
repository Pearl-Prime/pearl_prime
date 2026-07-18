# W0 Pilot — Formula-4 Generalization (2026-07-05)

**Branch:** `agent/naming-formula4-generalize-w0-20260705`  
**Scope:** Packaging layer only — no composer/atoms/12-shape changes.

## Engine generalization

| Change | File:line |
|--------|-----------|
| `formula4=True` at standard generation | `phoenix_v4/naming/cli.py:73-81` |
| Formula-4 title templates prepended for every brand | `phoenix_v4/naming/generator.py:228-233` |
| Shared F4 default prefs (long persona subtitles) | `omega/title_entropy/subtitle_patterns.yaml:353-360` |
| Brand-parameterized regen | `scripts/catalog/brand_title_regen.py` |
| Waystream delegates to shared regen | `scripts/catalog/waystream_subtitle_regen.py` |

## Pilot brands (en_US)

| Brand | Plans | F4 before→after | Persona sub before→after | Distinct (title/sub/pair) |
|-------|-------|-----------------|---------------------------|---------------------------|
| `adhd_forge` | 845 | 0%→**100%** | 99.2%→**100%** | 845/845/845 |
| `stabilizer` | 824 | 0%→**100%** | 97.1%→**100%** | 824/824/824 |
| `stabilizer` keyword-inverted | — | **94.2%→0%** | — | — |

Reports: `artifacts/naming/{adhd_forge,stabilizer}/title_regen_report.json`

## Stabilizer — 10 before→after pairs (sample)

| Old title | New title | Old subtitle | New subtitle |
|-----------|-----------|--------------|--------------|
| `Anxiety: Comparison` | `The Comparison Trap: A Guide to Anxiety` | `A guide for Corporate Managers` | `A Real Talk Guide to Anxiety for Managers` |
| `Anxiety: Comparison` (1hr) | `The Alarm Is Lying: Anxiety and Measuring Yourself Against Everyone` | `A guide for Corporate Managers` | `A Field Guide for Managers Navigating Anxiety` |
| `Anxiety: False Alarm` | `When Your Mind Screams Danger: A Guide to Anxiety` | `A guide for Corporate Managers` | `The False Alarm Response for Managers` |
| `Anxiety: Grief` | `The Weight You Carry: A Guide to Anxiety` | `A guide for Corporate Managers` | `How Managers Are Rewriting the Rules of Anxiety` |
| `Anxiety: Grief` (1hr) | `The Alarm Is Lying: Anxiety and The Grief That Doesn't Leave` | `A guide for Corporate Managers` | `A One-Hour Reset Through The Weight You Carry for Managers` |
| `Anxiety: Overwhelm` | `The Alarm Is Lying: Anxiety` | `A guide for Corporate Managers` | `Practical Tools to Regain Control When Life Feels Unmanageable for Managers` |
| `Overthinking: Overwhelm` | `When Everything Is Too Much: A Guide to Overthinking` | `A guide for Gen X Sandwich` | `A Real Talk Guide to Overthinking for Gen X Sandwich` |
| `Overthinking: Shame` | `The Hidden Weight of Shame: Overthinking` | `A guide for Gen X Sandwich` | `A Field Guide for Gen X Sandwich Navigating Overthinking` |
| `Burnout: Spiral` | `Escaping the Mental Loop: Burnout` | `A guide for Healthcare RNs` | `A Field Guide to The Spiral for Healthcare RNs` |
| `Financial Stress: Watcher` | `The Witnessing Practice: Financial Stress` | `A guide for Millennial Women Professionals` | `A Field Guide to The Watcher for Millennial Women Professionals` |

## adhd_forge — 10 before→after pairs (sample)

Many adhd_forge cells were partially authored; regen normalized apostrophes and enforced distinctness across 845 rows.

| Old title | New title | Old subtitle | New subtitle |
|-----------|-----------|--------------|--------------|
| `The Comparison Trap: A Guide to Anxiety` | *(unchanged hook)* | `A Real Talk Guide to Anxiety for Managers` | *(unchanged)* |
| `When Your Mind Screams Danger: A Guide to Anxiety` | *(unchanged)* | `A Field Guide for Managers Navigating Anxiety` | *(unchanged)* |
| `The Alarm Is Lying: Anxiety and Living with What You''ve Lost` | `The Alarm Is Lying: Anxiety and Living with What You've Lost` | `The Grief That Doesn't Leave — Anxiety for Managers` | *(unchanged)* |
| `The Alarm Is Lying: Anxiety and Carrying What You Can''t Say` | `The Alarm Is Lying: Anxiety and Carrying What You Can't Say` | `The Hidden Weight of Shame — Anxiety for Managers` | *(unchanged)* |
| `False Alarm` | `Misreading the Danger Signal: A Guide to Overthinking` | *(long prose sub)* | `A Field Guide for Gen Z Professionals Navigating Overthinking` |
| `Overthinking: Overwhelm` | `When Everything Is Too Much: A Guide to Overthinking` | `A guide for Gen X Sandwich` | `Practical Overthinking Tools for Gen X Sandwich` |
| `Burnout: Shame` | `The Hidden Weight of Shame: Burnout` | `A guide for Working Parents` | `A Real Talk Guide to Burnout for Working Parents` |
| `Imposter Syndrome: Spiral` | `Escaping the Mental Loop: Imposter Syndrome` | `A guide for Gen Z Professionals` | `A One-Hour Reset Through The Spiral for Gen Z Professionals` |
| `Somatic Healing: Watcher` | `The Witnessing Practice: Somatic Healing` | `A guide for Corporate Managers` | `A Field Guide to The Watcher for Managers` |
| `Financial Stress: Comparison` | `The Comparison Trap: A Guide to Financial Stress` | `A guide for Tech Finance Burnout` | `How Tech Finance Burnout Are Rewriting the Rules of Financial Stress` |

## HOLD

- **34 remaining en_US canonical brands** — await operator approval of this pilot before wave.
- **All non-en locales** — W3+ (localization BUILD).
- **Series-name engine** — W1 (BUILD).
- **Cover batches** — W2 (re-run after titles land).
- **12-shape content rebuild** — remains product priority; packaging runs in parallel.

## PR split note

Full-brand regen must run in a **single apply** for cross-brand distinctness. For governance (≤500 files/PR), commit plan YAMLs in file batches; use `brand_title_regen.py --batch b` only after batch a is on disk (sibling-batch seeding in script).
