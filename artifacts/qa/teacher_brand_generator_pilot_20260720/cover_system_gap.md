# Cover system vs teacher_originated brands

Confirmed: brand-driven cover treatment (`render_kdp_cover` / `abstract_cover_art`) keys off
`brand_id` + brand registry fields. Teacher-originated brands carry `cover_art_identity` in
`teacher_originated_brands.yaml` and are mirrored into `teacher_originated_brands.json` for
matchBrand. No new cover pipeline was built.

Gap (report-only): if a production cover path reads *only* `global_brand_registry_unified.yaml`
and ignores the teacher-originated registry, teacher_originated brand_ids would fall through
to defaults. Follow-up: confirm cover resolver merges teacher_originated the same way
`_brands_index()` / `matchBrand` now do.
