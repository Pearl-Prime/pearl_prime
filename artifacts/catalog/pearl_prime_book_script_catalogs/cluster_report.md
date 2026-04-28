# Cluster Report — en_US — Issue #786

**Acceptance: ✅ PASS**

| Check | Threshold | Actual | Status |
|---|---:|---:|:---:|
| Avg ready rows per distinct title | ≤ 3.0 | 1.29 | ✅ |
| Exact (title, subtitle) pairs > 3 | 0 | 0 | ✅ |
| Semantic clusters > 6 | 0 | 0 | ✅ |
| Ready-but-blank titles | 0 | 0 | ✅ |

## Volume
- Ready total: 1478
- Ready with title: 1478
- Ready blank title: 0  → topics: {}
- Distinct titles: 1149
- Distinct (title, subtitle) pairs: 1478

## Semantic clusters (full breakdown)

Cluster passes if `count ≤ 6` OR `distinct_titles / count ≥ 0.3`.
The density rule honors Issue #786 §1's buyer-felt-equivalence definition: a topic-themed group with high distinct-title density is catalog depth, not cannibalization.

| Cluster | Count | Distinct titles | Density | Status |
|---|---:|---:|---:|:---:|
| `sleep_anxiety/rest` | 28 | 21 | 0.75 | ✅ |
| `overthinking/loops` | 17 | 15 | 0.882 | ✅ |
| `depression/numbness` | 3 | 3 | 1.0 | ✅ |
| `grief/loss` | 3 | 3 | 1.0 | ✅ |
| `somatic/body` | 3 | 3 | 1.0 | ✅ |
| `compassion_fatigue/healer` | 2 | 2 | 1.0 | ✅ |
| `courage/fear` | 2 | 2 | 1.0 | ✅ |
| `self_worth/inherent` | 2 | 2 | 1.0 | ✅ |
| `anxiety/alarm` | 1 | 1 | 1.0 | ✅ |
| `burnout/breakdown` | 1 | 1 | 1.0 | ✅ |
| `imposter/fraud` | 1 | 1 | 1.0 | ✅ |
