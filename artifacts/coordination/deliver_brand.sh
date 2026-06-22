#!/usr/bin/env bash
# Reusable per-brand delivery: apply retitles (if any) -> verify -> render zero-GPU covers
# -> deploy to served path -> regenerate authored-only dashboard. Run from repo root.
#   bash artifacts/coordination/deliver_brand.sh <brand>
set -e
BRAND="$1"
cd "$(git rev-parse --show-toplevel)"

# 1. apply retitles if present
if [ -f "/tmp/${BRAND}_retitled.json" ]; then
  PYTHONPATH=. python3 - "$BRAND" <<'PY'
import json, yaml, os, sys
brand=sys.argv[1]
rt=json.load(open(f"/tmp/{brand}_retitled.json"))
n=0
for r in rt:
    p=f"config/source_of_truth/book_plans_en_us/{r['book_id']}.yaml"
    if not os.path.exists(p): print("MISSING", r['book_id']); continue
    d=yaml.safe_load(open(p)); d["title"]=r["title"]; d["subtitle"]=r["subtitle"]
    open(p,"w").write(yaml.safe_dump(d,sort_keys=False,allow_unicode=True)); n+=1
print(f"applied {n} retitles")
PY
fi

# 2. verify (distinct, clusters, remnants, bylines)
PYTHONPATH=. python3 - "$BRAND" <<'PY'
import glob, yaml, sys
from collections import Counter
brand=sys.argv[1]
LEG=["created_at","main_character_name","main_character_lora_id","confidence","plan_source_path"]
books=[yaml.safe_load(open(f)) for f in glob.glob(f"config/source_of_truth/book_plans_en_us/{brand}__*.yaml")]
books=[b for b in books if b.get("_needs_authoring") is False]
titles=[b["title"] for b in books]
def fw(t):
    ws=t.split(); return ws[1].lower() if ws and ws[0].lower() in {"the","a","an"} and len(ws)>1 else (ws[0].lower() if ws else "")
clusters={k:v for k,v in Counter(fw(b["title"]) for b in books).items() if v>=3}
dupes={t:c for t,c in Counter(titles).items() if c>1}
rem=sum(1 for b in books if any(k in b for k in LEG))
nob=sum(1 for b in books if not (b.get("author_positioning") or {}).get("byline_author"))
print(f"VERIFY {brand}: authored={len(books)} distinct={len(set(titles))} dupes={dupes or 0} clusters>=3={clusters or 0} remnants={rem} missing_byline={nob}")
assert not dupes and not rem and not nob, "VERIFY FAILED"
PY

# 3. render covers + contact (zero-GPU)
PYTHONPATH=. python3 -m scripts.publish.brand_covers.render_brand --brand "$BRAND" --all 2>&1 | tail -1
PYTHONPATH=. python3 -m scripts.publish.brand_covers.render_brand --brand "$BRAND" --contact 2>&1 | tail -1

# 4. deploy authored covers to served path
PYTHONPATH=. python3 - "$BRAND" <<'PY'
import glob, yaml, shutil, sys
from pathlib import Path
brand=sys.argv[1]
src=Path(f"artifacts/covers/{brand}/all"); dst=Path(f"brand-wizard-app/public/assets/covers/{brand}"); dst.mkdir(parents=True,exist_ok=True)
ids=[yaml.safe_load(open(f))["book_id"] for f in glob.glob(f"config/source_of_truth/book_plans_en_us/{brand}__*.yaml") if yaml.safe_load(open(f)).get("_needs_authoring") is False]
n=sum(1 for b in ids if (src/f"{b}.png").exists() and (shutil.copy2(src/f"{b}.png", dst/f"{b}.png") or True))
print(f"deployed {n}/{len(ids)} covers")
PY

# 5. regenerate authored-only dashboard
PYTHONPATH=. python3 scripts/onboarding/gen_brand_catalogs.py --brand "$BRAND" 2>&1 | tail -1
