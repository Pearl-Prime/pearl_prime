# Music Brand Diversity Gate Report (G1-G8)

brand_id=ahjan_music
batch_id=20260721
musician_id=ahjan
quality_profile=production
phase=phase_a_degraded
n_books=0
overall=PASS

## Gates

- **G1** (HARD_FAIL) — status=pass
  - note: per-slot-pool variant reuse against the source atom bank (Phase-A anti-copy-paste check)
  - LYRIC_BESTSELLER_BEAT: n=9 limit=5 max_reuse=1 violation=False
  - LYRIC_CLOSING: n=9 limit=5 max_reuse=1 violation=False
  - LYRIC_OPENING: n=9 limit=5 max_reuse=1 violation=False
  - MUSIC_REFLECTION_BESTSELLER_BEAT: n=9 limit=5 max_reuse=1 violation=False
  - MUSIC_REFLECTION_CLOSING: n=9 limit=5 max_reuse=1 violation=False
  - MUSIC_REFLECTION_OPENING: n=9 limit=5 max_reuse=1 violation=False
- **G2** (HARD_FAIL) — status=skipped
  - note: insufficient N (0 catalog book-plan rows < 50); Phase-A degraded mode — G1 (per-slot-pool / per-chapter reuse) is the only gate meaningful at this scale; catalog-scale gates skipped rather than false-passed on tiny data
- **G3** (HARD_FAIL) — status=skipped
  - note: insufficient N (0 catalog book-plan rows < 50); Phase-A degraded mode — G1 (per-slot-pool / per-chapter reuse) is the only gate meaningful at this scale; catalog-scale gates skipped rather than false-passed on tiny data
- **G4** (HARD_FAIL) — status=skipped
  - note: insufficient N (0 catalog book-plan rows < 50); Phase-A degraded mode — G1 (per-slot-pool / per-chapter reuse) is the only gate meaningful at this scale; catalog-scale gates skipped rather than false-passed on tiny data
- **G5** (HARD_FAIL) — status=skipped
  - note: insufficient N (0 catalog book-plan rows < 50); Phase-A degraded mode — G1 (per-slot-pool / per-chapter reuse) is the only gate meaningful at this scale; catalog-scale gates skipped rather than false-passed on tiny data
- **G6** (WARN) — status=skipped
  - note: insufficient N (0 catalog book-plan rows < 50); Phase-A degraded mode — G1 (per-slot-pool / per-chapter reuse) is the only gate meaningful at this scale; catalog-scale gates skipped rather than false-passed on tiny data
- **G7** (WARN) — status=skipped
  - note: insufficient N (0 catalog book-plan rows < 50); Phase-A degraded mode — G1 (per-slot-pool / per-chapter reuse) is the only gate meaningful at this scale; catalog-scale gates skipped rather than false-passed on tiny data
- **G8** (WARN) — status=skipped
  - note: insufficient N (0 catalog book-plan rows < 50); Phase-A degraded mode — G1 (per-slot-pool / per-chapter reuse) is the only gate meaningful at this scale; catalog-scale gates skipped rather than false-passed on tiny data

## Limitations

Phase-A degraded mode: this brand has no catalog-scale book-plan data yet (0 rows found), so G2-G8 are reported skipped rather than fabricated as passing — see DO NOT list in docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/04_Pearl_Dev_diversity_ci_guard.md.

