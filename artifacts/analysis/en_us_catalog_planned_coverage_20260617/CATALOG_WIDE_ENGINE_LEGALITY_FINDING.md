# en_US catalog-wide engine-legality finding (origin/main 29c3fd76bc)

**Date:** 2026-06-17  ·  **Agent:** Pearl_Prime  ·  **Status:** DISCOVERY (flagged; only devotion_path fixed in this PR)

The §5 anxiety-triad mis-pointing is **NOT unique to devotion_path** — the same pattern
(`{false_alarm, overwhelm, spiral}` cross-applied to non-anxiety topics) is present across
**all 8 en_US brands** on origin/main. Each (brand×persona×topic) was seeded with the same 3
anxiety engines regardless of topic; for non-anxiety topics some are legal, some forbidden,
and the topic's OTHER legal engines (watcher/grief/shame/comparison) were never planned.

| brand | legal_planned | missing_legal | ILLEGAL_planned | planned% (of legal arc-backed) |
|---|--:|--:|--:|--:|
| cognitive_clarity | 43 | 75 | 88 | 36.4% |
| devotion_path | 31 | 54 | 66 | 36.5% |
| digital_ground | 50 | 62 | 77 | 44.6% |
| heart_balance | 20 | 60 | 77 | 25.0% |
| sleep_restoration | 53 | 0 | 55 | 100.0% |
| solar_return | 50 | 40 | 44 | 55.6% |
| somatic_wisdom | 30 | 40 | 110 | 42.9% |
| stillness_press | 130 | 0 | 55 | 100.0% |
| **TOTAL** | **407** | **331** | **572** | **55.1%** |

## Why only devotion_path is fixed in this PR

1. **Spec scope:** `DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md` + the workstream +
   the §5 re-point map are devotion_path-scoped. No merged spec authorizes a catalog-wide re-point.
2. **Naming-engine config is devotion-only:** #1677 added persona_title_flavor + subtitle_patterns
   brand prefs ONLY for devotion_path. Re-pointing the other 7 brands with *naming-engine* titles
   (the binding) at devotion quality would first require replicating #1677's per-brand naming
   config for 7 brands — that is a naming-engine lane (Pearl_Editor), not catalog_planning, and
   the engine produces degraded output for them today (broken `{}` substitution, unnamed persona).
3. **WRITE_SCOPE + time-box:** this re-dispatch's declared scope is devotion_path; a 903-plan,
   multi-subsystem rewrite would exceed it.

## Recommended follow-on (operator decision)

Open a **catalog-wide engine-legality reconciliation** spec (generalize the devotion §5 map per
`topic_engine_bindings.yaml`) + a **naming-engine per-brand config** workstream (replicate #1677's
persona_title_flavor + subtitle_patterns for the other 7 brands) BEFORE re-pointing them, so all
titles stay naming-engine-sourced. Until then, the 7 brands carry 506 illegal-engine plans on main.
