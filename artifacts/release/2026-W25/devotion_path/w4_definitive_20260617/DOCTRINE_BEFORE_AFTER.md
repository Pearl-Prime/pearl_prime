# Real-Doctrine Resolution — before/after (#1700)

**Claim proven:** on the fully-right base (`aaebe0cdc4`, contains #1700), the `TEACHER_DOCTRINE`
slots of every devotion book resolve to **real `sai_ma_TEACHER_DOCTRINE_*` atoms**, not the
~26-word `sai_ma_COMPRESSION_*` fragments the pipeline silently fell back to before #1700 landed.

## The two atom banks (measured on the snapshot)

| Bank | n | word range | median | role |
|---|---|---|---|---|
| `sai_ma_TEACHER_DOCTRINE_*` (#1700) | 12 | **333–378** | 353 | full Sai Maa teaching — the doctrine slot's intended content |
| `sai_ma_COMPRESSION_*` (pre-#1700 fallback) | 12 | 19–31 | 26 | terse compressions — ~13× thinner |

## Prose contrast (same teacher, same topic)

**`sai_ma_TEACHER_DOCTRINE_000` (337 words):**
> Sai Maa teaches that the Divine Mother is not a story told to comfort children. She is not a
> metaphor for kindness, not a poetic name for nature, not a figure painted on a temple wall. She
> is a living presence, and She is awake inside you while you read this. …

**`sai_ma_COMPRESSION_002` (25 words) — the old degraded fill:**
> The shakti is already awake in you. You do not need to create it. You need to stop suppressing
> it. Liberation is subtraction, not addition.

## Resolution evidence (atom IDs that filled the doctrine slots)

Measured from each book's `selected_content_variants.json` / `enrichment_audit.json`:

| Base | doctrine-slot atom IDs | verdict |
|---|---|---|
| OLD `692b27d919` (no #1700), `burnout/overwhelm/corporate_managers` | `sai_ma_COMPRESSION_{002,003,004,005,006,008,009,012}` — **0 TEACHER_DOCTRINE** | degraded |
| NEW `aaebe0cdc4` (#1700), `courage/false_alarm/corporate_managers` | `sai_ma_TEACHER_DOCTRINE_{000,001,002,005,008,009,010,011}` — **0 COMPRESSION** | real doctrine |

Per-cell resolution across the whole wave: `DOCTRINE_RESOLUTION.tsv`.

## Secondary unlock — courage now builds at all

Pre-#1700, `courage` was **0/11 buildable** (hard `EnrichmentGapError: TEACHER_DOCTRINE`) and
`imposter_syndrome` was 1/11; the doctrine pool was persona-scoped. #1700 made the sai_ma doctrine
a **shared teacher pool**, so it covers every `persona × topic × engine` devotion cell at once —
lifting the "~20 buildable subset" cap that bounded the earlier proof wave (PR #1698).
