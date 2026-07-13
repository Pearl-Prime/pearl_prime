# Localization Prep 14-Pack — Canonical Truth Packet (2026-07-13)

**Purpose:** Single source of truth that all downstream locale translation waves
reference before claiming completion. Locks the real 14-language roster, the
sanctioned provider path, the validator path, glossary truth, and current live
coverage baseline.

**Authority order:** if any other doc disagrees with this packet on roster,
provider, or validator truth, this packet wins (dated 2026-07-13) unless a
later-dated packet supersedes it. Config files (`locale_registry.yaml`,
`content_roots_by_locale.yaml`) remain the underlying schema authority; this
packet is the operational summary layered on top of them.

---

## 1. Canonical 14-language roster

Verified against `config/localization/locale_registry.yaml` and
`config/localization/content_roots_by_locale.yaml` on `origin/main` — **all 14
locale keys present in both files**:

| Locale | Language | Region | Bucket | TTS primary |
|---|---|---|---|---|
| en-US | English | United States | baseline (source, not a translation target) | ElevenLabs |
| ja-JP | Japanese | Japan | CJK6 | CosyVoice2 |
| ko-KR | Korean | South Korea | CJK6 | CosyVoice2 |
| zh-CN | Chinese (Simplified) | Mainland China | CJK6 | CosyVoice2 |
| zh-TW | Chinese (Traditional) | Taiwan | CJK6 | CosyVoice2 |
| zh-HK | Chinese (Traditional/Cantonese) | Hong Kong | CJK6 | CosyVoice2 (yue-HK) |
| zh-SG | Chinese (Simplified) | Singapore | CJK6 | CosyVoice2 |
| es-US | Spanish (neutral LatAm) | US Hispanic market | European/LatAm bucket | ElevenLabs |
| es-ES | Spanish (Castilian) | Spain | European/LatAm bucket | ElevenLabs |
| fr-FR | French | France | European/LatAm bucket | ElevenLabs |
| de-DE | German | Germany/DACH | European/LatAm bucket | ElevenLabs |
| it-IT | Italian | Italy (EU catalogue) | European/LatAm bucket | ElevenLabs |
| hu-HU | Hungarian | Hungary (EU catalogue) | European/LatAm bucket | **ElevenLabs only** — Google Neural2 does not support Hungarian |
| pt-BR | Portuguese | Brazil | 14th locale (Q-MANGA-01, ratified OPD-20260704-005, 2026-07-04) | Google Neural2 |

**pt-BR is explicitly in scope** — confirmed live in both registry files, and
hardcoded into the canonical locale tuples in `scripts/localization/run_translation_loop.py`
(`EUROPEAN_LOCALES` includes `pt-BR`) and `scripts/ci/report_translation_coverage.py`.
`run_locale_batches.py` states the canon explicitly: *"pt-PT and ru-RU are NOT
in the canon (no locale_registry.yaml entry) — do not re-add without first
registering the locale there."*

### Stale docs overridden

- **`docs/TRANSLATE_QWEN_PIPELINE_CLI.md`** (last updated 2026-03-04) lists
  only **13** locales (missing pt-BR) and labels itself "all 13 locales" in
  §4. This is **stale** — pt-BR was ratified 2026-07-04, four months after
  this doc's last update. Per the mission's roster override, treat this doc's
  locale table as superseded by this packet; do not re-derive the roster from
  it.
- No other roster-bearing doc found in scope that omits pt-BR or adds an
  unratified locale (pt-PT, ru-RU checked — correctly absent).

---

## 2. Sanctioned provider path (Tier 2, unattended-safe)

**Entry points (atom/bestseller translation):**
- `scripts/localization/run_translation_loop.py` — the comparator loop
  (English atom → Qwen translate → Qwen judge → patch/retry → pass or
  manual_review). Covers both CJK6 and the 7 European/LatAm locales +
  pt-BR (`ALL_LOCALES = CJK6_LOCALES + EUROPEAN_LOCALES`, 13 non-English targets).
- `scripts/localization/cjk_enqueue_translate.py` — **queue-first** dispatch
  for CJK locales via `pscli`/Procrastinate (RAP-compliant): "Never calls
  Ollama directly — routes through `llm_translate_atoms_batch` worker."
  Falls back to SSH to Pearl Star if `pscli` isn't on local PATH.
- `scripts/localization/llm_client.py` — the underlying provider-resolution
  module both of the above use.

**Provider resolution (verified in `llm_client.py`):**
- **Default / Tier-2 path:** Ollama on Pearl Star, model `qwen2.5:14b`
  (`qwen3:14b` is *not* installed — `qwen2.5:14b` is the actual live default;
  do not assume the config-file model ID without checking the live-default
  comment in `llm_client.py`).
- **Cloud is opt-in only, never silent:** `PHOENIX_TRANSLATION_ALLOW_CLOUD=1`
  gates every nonlocal path. Without it, DeepSeek/Together/Gemini/Cloudflare/
  DashScope keys — even if present in the Keychain-loaded env — are never
  consulted. Direct module comment: *"Paid/banned cloud keys in a
  Keychain-loaded env must NEVER silently win over Ollama."*
  `run_translation_loop.py` independently enforces the same rule at its own
  call site (refuses to route to paid keys if no Ollama endpoint and no
  explicit cloud opt-in — raises rather than falling through).
- **Cloud provider chain (opt-in only, when explicitly enabled):** DeepSeek →
  Together AI → Google AI (Gemini) → Cloudflare Workers AI (Gemma 3 12B) →
  DashScope, in that fallback order. All are flagged in-code as "opt-in
  only" / "banned by default policy" (DashScope specifically noted as
  "banned by default policy" pending active billing).
- **This matches CLAUDE.md's LLM Tier Policy** — Tier 2 = Gemma(English)/Qwen(CJK6)
  via Ollama, unattended-safe, no silent paid fallback.

**Gap flagged, not fixed this session:** there is a dedicated queue-first
`pscli` enqueue wrapper for CJK (`cjk_enqueue_translate.py`) but **no
equivalent dedicated queue-first wrapper for the 7 European/LatAm locales +
pt-BR** — they route through `run_translation_loop.py`'s direct
`llm_client.py` call, which is still Tier-2/Ollama-default and RAP-safe-by-default,
but is not the `pscli` queue-dispatch pattern CJK uses. Per RAP
(`docs/ROBUST_AGENT_PROTOCOL.md`), any single European-locale translation call
is typically short (<10s per shard per `run_locale_batches.py`'s "~20s per
LLM call" note), so this is flagged as a real gap for anyone batching large
unattended European waves, not a blocker for small/manual runs.

**Separate entrypoint — do not conflate:** `scripts/localization/run_locale_batches.py`
targets **Pearl News article-topic translation** (`climate`, `economy_work`,
`education`, `inequality`, `mental_health`, `partnerships`, `peace_conflict` —
not the bestseller atom topic set) via a "Route 1: Claude meta-prompt → Qwen"
(CJK) / "Route 2: Claude direct" (European) split, with its own LM Studio /
DashScope preflight. It uses the same canonical 14-locale set but is a
different pipeline from atom/bestseller translation — do not report Pearl
News locale coverage as bestseller-atom coverage or vice versa.

---

## 3. Validator path

- `scripts/localization/validate_translations.py` — quality validation using
  the Qwen judge model against the same `native_regional_language_fit` rubric
  used by the audiobook comparator loop. Checks: semantic fidelity, native
  language fit, cultural adaptation, atom constraints (40–80 words,
  news-connectable, tradition-specific). Config:
  `config/localization/translation_loop_config.yaml`; checklist:
  `config/localization/translation_checklist.yaml`.
- `scripts/localization/locale_structural_gate.py` — structural gate (schema/shape).
- `scripts/localization/validate_cjk_atom.py` — CJK-specific atom validator.
- `scripts/check_golden_translation.py` — golden-regression check against
  `config/localization/quality_contracts/golden_translation_regression.yaml`.
- `scripts/localization/teacher_bank_locale_parity.py` — teacher-bank
  locale-parity check.
- Release gating thresholds: `config/localization/quality_contracts/release_thresholds.yaml`.

---

## 4. Glossary / terminology truth

**File:** `config/localization/quality_contracts/glossary.yaml`
(schema_version 1.0)

**Live content, verified:** **10 core brand terms × 6 CJK locales = 60
translation entries.** Header comment confirms this is the intended scope:
*"Canonical glossary for translation quality. 10 core brand terms × 6 CJK
locales × 60 entries."*

**Real gap — flag, do not fabricate:** the glossary has **zero entries for
the 7 European/LatAm locales** (es-US, es-ES, fr-FR, de-DE, it-IT, hu-HU,
**pt-BR included**). No European-locale glossary file exists elsewhere in
`config/localization/` (checked directory listing — only the one CJK6
`glossary.yaml`). This means:
- The 10 core brand terms (nervous system / the alarm / the mask / the
  pattern / the strategy / the cost / somatic / etc.) have **no ratified
  European-locale translation** for terminology-consistency checking.
- Any European-locale translation wave currently has no glossary-based
  quality contract to validate against, unlike CJK6 waves.
- This is a **volume/authoring gap** (7 locales × 10 terms = 70 entries to
  add, following the exact same schema), not a wiring or governance gap —
  the schema and validator plumbing already generalize (glossary.yaml is a
  flat locale-keyed dict per term; no code changes needed to add locale
  keys). Flagged here as a **remaining true blocker** for downstream
  European-locale waves, not authored in this session (scope was truth-lock,
  not new content authoring).

---

## 5. Live coverage baseline (2026-07-13, verified against `origin/main`)

**Method:** ran `scripts/ci/report_translation_coverage.py --locales
<all 13 non-English targets> --json` against a clean `git archive
origin/main` extraction (the primary working tree had ~283k dirty status
lines from pre-existing shared-tree churn across sibling sessions — unrelated
to this branch — so coverage was measured from a clean copy, not the dirty
working tree, to avoid false-low readings from locally-missing files).
Full JSON: `artifacts/qa/locale_prep_14pack_20260713/coverage_baseline.json`.

**English source baseline:** 3,754 `CANONICAL.txt` files across the 5
bestseller slot types (PIVOT, TAKEAWAY, THREAD, PERMISSION, STORY) + 7 engine
directories (comparison, false_alarm, grief, overwhelm, shame, spiral, watcher).

| Locale | Translated files | Coverage | Note |
|---|---:|---:|---|
| zh-TW | 3,600 / 3,754 | **95.9%** | near-complete |
| ja-JP | 3,164 / 3,754 | **84.3%** | near-complete |
| zh-CN | 1,622 / 3,754 | **43.2%** | mid-volume, needs next wave |
| ko-KR | 248 / 3,754 | **6.6%** | pilot-only |
| zh-HK | 259 / 3,754 | **6.9%** | pilot-only |
| zh-SG | 255 / 3,754 | **6.8%** | pilot-only |
| es-US | 82 / 3,754 | **2.2%** | pilot foothold |
| pt-BR | 82 / 3,754 | **2.2%** | pilot foothold |
| es-ES | 0 / 3,754 | **0.0%** | not started |
| fr-FR | 0 / 3,754 | **0.0%** | not started |
| de-DE | 0 / 3,754 | **0.0%** | not started |
| it-IT | 0 / 3,754 | **0.0%** | not started |
| hu-HU | 0 / 3,754 | **0.0%** | not started |

These numbers are consistent with the ranges already cited in
`docs/PROGRAM_STATE.md` §Localization (ja-JP ~84%, zh-TW ~96%, zh-CN ~43%,
ko-KR ~6%) — no contradiction found; this packet adds the previously-uncited
zh-HK/zh-SG/European/pt-BR figures.

**Caveat on this script's `by_locale` (native-check) section:** it returned
`persona_topic_count: 0, has_atoms: false` for every locale when run from the
archived clean tree — this is a `sys.path` package-root artifact of running
`check_native_check` from a `git archive` extraction rather than a full
checkout (`No module named 'scripts'` internal error, visible in the raw
JSON), **not** a real zero-coverage signal. The `bestseller` section (used
for the table above) does not depend on that submodule and is trustworthy.

---

## 6. Per-locale wave ordering (recommended, sourced from existing docs — not newly invented)

Derived from `content_roots_by_locale.yaml` phase/status notes + the live
coverage baseline above:

1. **zh-TW (95.9%), ja-JP (84.3%)** — near-complete; next action is
   validation/polish passes (`validate_translations.py` + golden regression),
   not new-volume translation waves.
2. **zh-CN (43.2%)** — mid-volume; highest-leverage next full wave (largest
   remaining-gap CJK6 locale with real traction already).
3. **ko-KR (6.6%), zh-HK (6.9%), zh-SG (6.8%)** — pilot-only; `content_roots_by_locale.yaml`
   marks zh-HK `population_status: planned` and explicitly flags zh-SG for
   ROI evaluation before a full build ("English dominates Singapore
   commerce"). Treat these three as the next CJK6 wave tier, zh-SG lowest
   priority pending an explicit ROI/binding decision.
4. **fr-FR** — `content_roots_by_locale.yaml`'s pt-BR entry explicitly notes
   *"14th locale (Q-MANGA-01); M7 Wave A after fr_FR"* — i.e. the existing
   roadmap already sequences fr-FR before pt-BR. fr-FR is currently at 0%
   despite this; it is the naturally-next European locale to start.
5. **pt-BR (2.2% foothold)** — per the same note, continue after fr-FR
   reaches meaningful coverage; it already has a pilot foothold to build on.
6. **de-DE** — `content_roots_by_locale.yaml` calls it "the largest European
   audiobook market" — high-leverage once fr-FR/pt-BR are underway.
7. **es-ES, es-US (2.2% foothold), it-IT** — es-US already has the same
   foothold as pt-BR; es-ES is the Castilian-market sibling and currently
   zero; it-IT is EU-catalogue-tagged but zero.
8. **hu-HU** — smallest EU-catalogue market, ElevenLabs-only TTS constraint
   (Google Neural2 does not support Hungarian per registry note); lowest
   priority in this bucket.

This ordering is a recommendation for sequencing, not a hard gate — any
operator-directed reprioritization overrides it.

---

## 7. Files this packet is built from (verify-again pointers for downstream waves)

- `config/localization/locale_registry.yaml` — locale schema authority
- `config/localization/content_roots_by_locale.yaml` — content root + phase-note authority
- `config/localization/quality_contracts/glossary.yaml` — glossary (CJK6-only, gap noted above)
- `config/localization/quality_contracts/translation_checklist.yaml`
- `config/localization/quality_contracts/golden_translation_regression.yaml`
- `config/localization/quality_contracts/release_thresholds.yaml`
- `config/localization/translation_loop_config.yaml` — model config (draft/judge, cloud/local IDs)
- `scripts/localization/run_translation_loop.py` — main comparator-loop entrypoint (all 13 non-English targets)
- `scripts/localization/cjk_enqueue_translate.py` — CJK queue-first (`pscli`) dispatch
- `scripts/localization/llm_client.py` — provider resolution (Ollama-default, cloud opt-in only)
- `scripts/localization/validate_translations.py` — Qwen-judge quality validator
- `scripts/ci/report_translation_coverage.py` — coverage report (source of §5 numbers)
- `artifacts/qa/locale_prep_14pack_20260713/coverage_baseline.json` — raw baseline JSON from this session

---

## 8. Acceptance checklist (this packet)

- [x] Canonical 14-language roster verified against live `origin/main` config (not memory/docs alone)
- [x] pt-BR explicitly confirmed in scope, in every roster-bearing file checked
- [x] One stale doc identified and named (`TRANSLATE_QWEN_PIPELINE_CLI.md`, 13-locale table)
- [x] Sanctioned provider path verified in code: Tier-2 Ollama default, cloud strictly opt-in, never silent
- [x] Queue-first (CJK) vs direct-call (European) path distinction documented; gap flagged honestly
- [x] Validator path enumerated with config files
- [x] Glossary truth refreshed: CJK6 = 60 entries live; European 7-locale set (incl. pt-BR) = 0 entries, real gap, not fabricated
- [x] Live coverage baseline captured for all 13 non-English target locales, methodology and caveats documented
- [x] Wave ordering proposed, sourced from existing doc notes + live coverage, not invented from scratch
