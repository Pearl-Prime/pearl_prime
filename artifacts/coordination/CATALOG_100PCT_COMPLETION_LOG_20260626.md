# Catalog 100% Completion — Assumptions Log & Handoff

**Date:** 2026-06-26
**Goal:** All canonical en_US brands at ≥800 book plan YAMLs on `origin/main`.
**Operator will QA after.**

## Ground truth at dispatch (origin/main `1951ea3e`)

- **Total plans:** 20,161
- **Brands at 800+:** 22 / 40 canonical base brands
- **Remaining: 18 brands**

### Zero-plan brands (9) — need full ~800 each
hormone_reset, morning_momentum, spiritual_ground, trauma_path, longevity_lab,
healing_ground, minimal_mind, high_performer, stoic_edge

### Partial brands (9) — need top-up to 800
| brand | current | needs |
|---|---|---|
| legacy_builder | 736 | ~64 |
| resilient_parent | 558 | ~242 |
| career_lift | 556 | ~244 |
| creative_unfold | 376 | ~424 |
| relationship_clarity | 16 | ~784 |
| night_reset | 13 | ~787 |
| executive_calm | 13 | ~787 |
| optimizer | 8 | ~792 |
| calm_student | 7 | ~793 |

## Assumptions (operator: please verify in QA)

1. **Bridge is the canonical generator.** `gen_brand_catalog_plan_csv.py --brand X --out F`
   then `catalog_plan_csv_to_plan_yaml.py --csv F --brand X` produces 800 rows for ANY
   canonical brand, including zero-plan ones (verified live on `healing_ground` → 800 rows,
   9 personas × 15 topics, 238 1hr variants). No LLM at generation time.
2. **800 = the target per brand** (per the 800-books-per-brand program). Counts that exceed
   800 (e.g. 837) are from legacy origin-only files from prior schemes (#1685/#1802) which
   are NOT deleted (additive-only discipline).
3. **All new plans carry `runtime_format_id: standard_book_60min`** which is now in the
   format registry (PR #2002) → spine-buildable, no KeyError.
4. **`_needs_authoring: true`** on prose fields — these are STRUCTURAL skeletons. Prose
   authoring (Pearl_Writer wave) is a SEPARATE downstream step, not part of this completion.
5. **Pure-addition discipline:** never overwrite/delete a file already on origin/main. Each
   PR ≤180 files (governance warns >200, blocks >500).
6. **Series plans (`series_plans_en_us/`) are committed alongside book plans** (~128/brand,
   shared across a brand's books). Net-new only.

## Merge mechanics (hard constraints discovered this session)

- **`Protect main` ruleset:** PR REQUIRED (no direct push to main for anyone — bypass is
  `pull_request`-mode only). Required checks: **`Verify governance` + `parse-sweep`**.
- **Self-merge class:** additive skeleton PRs pass both checks; squash-merge, no `--admin`.
- **GITHUB_TOKEN-created PRs do NOT trigger the required checks** (and no PR-PAT secret
  exists) → a zero-touch GitHub Actions runner is blocked until a PAT secret is added.

## Execution

### Primary (running now): local background agents
4 hardened agents, proven pattern (idempotent net-new, ≤180-file plumbing PRs, unique
timestamped branches, poll both required checks 20 min, MERGED-retry, final self-sweep).
**Limitation: these run in the local Claude Code process — they DIE if the laptop closes /
process exits** (this is why a prior wave's agents C/D were lost). They are idempotent, so
re-dispatch resumes cheaply from whatever origin/main holds.

### Durable backstop (laptop-off-safe): GitHub Actions
`.github/workflows/catalog-fanout-complete.yml` — matrix per under-800 brand, runs the
bridge, chunks net-new into ≤180-file PRs, polls checks, merges. **Requires ONE operator
step:** add a repo secret `CATALOG_PAT` (a PAT with `repo` + `workflow` scope) so the PRs
it opens trigger `Verify governance`/`parse-sweep`. Then `gh workflow run catalog-fanout-complete.yml`.
Idempotent — safe to run anytime; completes whatever remains.

## Verification command (for QA)

```bash
git fetch origin --prune
python3 - <<'PYEOF'
import yaml, collections, subprocess
from pathlib import Path
r=subprocess.run(['git','ls-tree','-r','--name-only','origin/main','config/source_of_truth/book_plans_en_us/'],capture_output=True,text=True)
have=collections.Counter()
for l in r.stdout.splitlines(): have[Path(l).stem.split('__')[0]]+=1
reg=yaml.safe_load(Path("config/brand_management/global_brand_registry_unified.yaml").read_text())
LOC=['en_us','zh_tw','zh_cn','zh_hk','zh_sg','ja_jp','ko_kr','es_us','es_es','fr_fr','de_de','it_it','hu_hu','pt_br']
base=set()
for k in reg.get("brands",{}):
    b=k
    for loc in LOC:
        if b.endswith('_'+loc): b=b[:-(len(loc)+1)]; break
    base.add(b)
under=[(b,have.get(b,0)) for b in base if have.get(b,0)<800]
print(f"at 800+: {sum(1 for b in base if have.get(b,0)>=800)}/{len(base)} | under: {len(under)}")
for b,c in sorted(under,key=lambda x:x[1]): print(f"  {b}: {c}")
PYEOF
```
