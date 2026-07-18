# Semantic-dedup closeout (2026-07-08)

**Lane:** shipped-book EI v2 `content_uniqueness` calibration

## Root cause

Legacy chapter eval used atom-pool composite (35% ngram + 25% structure + 25% beat) with max_sim*2 penalty over others[:5]. Shipped books share therapeutic beat markers and paragraph rhythm; word n-gram overlap stays ~0.01 (trigram uniqueness=1.0). Beat similarity=1.0 inflated composite to ~0.42 → content_uniqueness≈0.16 uniformly.

## Burnout proof cells

| Cell | before avg | after avg |
|------|----------:|----------:|
| burnout_overwhelm__corporate_managers | 0.153 | 0.8047 |
| burnout_watcher__corporate_managers | 0.153 | 0.8047 |
| burnout_grief__corporate_managers | 0.153 | 0.8047 |

Duplicate control still flagged: True (score=0.0)

## Non-claims

- No writer/prose edits
- No registry-scoring changes
- Atom-pool dedup weights unchanged
