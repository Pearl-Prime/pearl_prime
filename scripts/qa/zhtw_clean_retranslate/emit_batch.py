import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emit import build_zh

specs = json.load(open(sys.argv[1], encoding="utf-8"))
base = sys.argv[2] if len(sys.argv) > 2 else "."
for spec in specs:
    en_path = os.path.join(base, spec["en_path"])
    out_path = os.path.join(base, spec["out_path"])
    build_zh(en_path, spec["translations"], out_path)
    print("wrote", out_path)
