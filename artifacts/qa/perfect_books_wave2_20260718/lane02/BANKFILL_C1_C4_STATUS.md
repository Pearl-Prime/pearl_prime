# Lane 02 — C1–C4 bank-fill status per cell

**Acceptance layer:** authored candidate ceiling (banks filled; NOT system working —
that is Lane 03's ONTGP job, gated on this signal).

## C1 — STORY pool (tuple viability)

All 3 cells were **already tuple-viable** before this lane touched anything (no C1
fill was required — verified, not assumed):

```
$ PYTHONPATH=. python3 phoenix_v4/gates/check_tuple_viability.py --persona <p> --topic burnout --engine overwhelm --format F006 --json
corporate_managers,burnout,overwhelm,F006   -> TUPLE_VIABLE
tech_finance_burnout,burnout,overwhelm,F006 -> TUPLE_VIABLE
healthcare_rns,burnout,overwhelm,F006       -> TUPLE_VIABLE
```

Full output: `tuple_viability_3cells.txt`.

## C2 — EXERCISE bank (production, no silent practice_library-only)

Verified per-cell EXERCISE atom pools already exist and are substantial (not thin):

| Persona | `atoms/<persona>/burnout/EXERCISE/CANONICAL.txt` |
|---|---|
| corporate_managers | 225 lines |
| tech_finance_burnout | 271 lines |
| healthcare_rns | 317 lines |

No C2 fill was required for these 3 cells. (`EXERCISE-BANK-RESOLUTION-01`'s
practice_library fallback warning was not observed in the corporate_managers /
tech_finance_burnout render logs prior to the G-DEF4 hard-stop.)

## C3 — Accent banks (`EXTERNAL_STORY`, `AUTHOR_COMMENTARY`, `WISDOM_ESSENCE`, `CITED_EVIDENCE`)

All 4 classes are **topic-keyed, not persona-keyed**
(`phoenix_v4/planning/accent_planner.py::_build_pools_with_provenance`), so one fill
pass on topic=`burnout` serves all 3 cells:

| Class | Path | Before | After | Action |
|---|---|---|---|---|
| `EXTERNAL_STORY` | `SOURCE_OF_TRUTH/accent_banks/external_stories/burnout_entries.yaml` | 17 entries (23 loaded incl. locale cluster rows) | unchanged | Already stocked — **no fill needed** |
| `CITED_EVIDENCE` | `SOURCE_OF_TRUTH/accent_banks/evidence/burnout/entries.yaml` | 10 entries | unchanged | Already stocked — **no fill needed** |
| `WISDOM_ESSENCE` | `SOURCE_OF_TRUTH/accent_banks/wisdom_essence/burnout/entries.yaml` | **missing (dir did not exist)** — `no_supply_pool` gap | **8 new entries authored** | **FILLED** — mirrors `wisdom_essence/anxiety/entries.yaml` shape exactly (essence_id/theme/topic_keys/doctrine_keys/source_teachers/source_refs/secular_safe/position_fit/dosage_class/register_variants.secular.body [3 paragraphs]/wisdom_traditions/tradition_attributed/depth_pattern) |
| `AUTHOR_COMMENTARY` | `SOURCE_OF_TRUTH/accent_banks/author_commentary/burnout/{ravi_chandra,lena_thorne}/en_US.yaml` | **missing (dir did not exist)** — `no_supply_pool` gap | **8 + 8 = 16 new commentaries authored** across 2 author files | **FILLED** (see author-routing note below) |

### Author-routing note (why 2 author files for AUTHOR_COMMENTARY)

`accent_planner.py` defaults `author_id` to `"ravi_chandra"` whenever no `--author` is
threaded through the CLI (`author_id=author_id or "ravi_chandra"`,
`_build_pools_with_provenance` call site) — this is what the actual four-piece-chord
render used in this lane resolves to today, so `author_commentary/burnout/ravi_chandra/en_US.yaml`
is the file that is **actually live-consumed by default**. `config/author_registry.yaml`
separately declares `daniel_voss` (persona_ids `[tech_finance_burnout,
corporate_managers]`, topic_ids `[burnout, imposter_syndrome]`, brand `stillness_press`)
and per-persona `way_stream_sanctuary` authors (`theo_castellan` for
corporate_managers×burnout, `ana_reyes` for tech_finance_burnout×burnout, `oscar_bello`
for healthcare_rns×burnout) as the *intended* author-resolution targets once the
"Pipeline use (when implemented)" TODO in that registry's own comments is wired up —
that wiring does not exist in code yet (composer-adjacent, out of scope for this
lane). `lena_thorne` (persona_ids `[millennial_women_professionals, healthcare_rns]`,
topic_ids `[anxiety, sleep_anxiety]`) does not formally cover `burnout` either; her
file was authored anyway (reusing her exact existing `bio_license_refs`, no new claims)
because she is the closest existing witness voice with `healthcare_rns` already in her
`persona_ids`, and will become correct once the registry's author-resolution TODO is
implemented for the `stillness_press` brand path. **Net effect: the bank gap is closed
under BOTH the current default-author code path (`ravi_chandra`) and the intended
future-wired author-resolution path for these personas.** No new author bios/claims
were invented; all `bio_license_refs` reuse the vocabulary already established in the
`anxiety` pilot banks.

Verified both new files parse, pass the secular-register lint
(`phoenix_v4.quality.composite_doctrine_secular_lint.lint_file_secular`, 0 violations),
and load through the real accent-planner loaders (`_load_wisdom_essence`,
`_load_author_commentary`) with non-empty pools. `WISDOM_ESSENCE` entries verified at
exactly 3 paragraphs per `secular.body` (the shape the spec's "3-para + secular" note
requires).

## C4 — Persona-registry routing (kill Gen-Z-as-default-fallback)

**Not fixed for `burnout` in this lane** — root-caused instead, and the root cause is
catalog-wide, not a `burnout`-specific or 3-cell-specific gap. See
`DEF4_SYSTEMWIDE_FINDING.md` for the full writeup, live-render evidence (106 drops,
`SystemExit(1)` on 2 of 3 cells actually rendered), and why a compliant "fill banks
only" fix does not exist within this lane's write scope (the correct fix requires
either destructively reassigning the shared `registry/burnout.yaml` away from
`gen_z_professionals × burnout` — not allowed, no pool may shrink — or a
persona-aware registry-loading code change, which is composer/wiring, banned for this
lane).

**Per-cell C4 status: BLOCKED (catalog-wide root cause), DEFERRED, not silenced.**
