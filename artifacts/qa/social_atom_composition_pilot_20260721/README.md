# Social atom composition pilot (2026-07-21)

- Cell: persona=`corporate_managers` topic=`burnout`
- Platforms/surfaces: linkedin_feed_portrait, instagram_feed_portrait
- Brands: stillness_press, cognitive_clarity
- Posts: 20 (target ≥20)

Regenerate:
```bash
python3 scripts/ci/check_social_post_variation.py \
  --write-pilot artifacts/qa/social_atom_composition_pilot_20260721
```

Similarity: 3-gram Jaccard (see check_prose_duplication.py).
Same-brand fail ≥ 0.72; cross-brand fail ≥ 0.9.
