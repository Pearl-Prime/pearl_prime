"""Generate per-author FLUX imagery pools on Pearl Star (schnell ONLY).

Only image-family authors need a pool (10 of 20). Reuses the proven pilot recipe
(scripts.publish.render_imagery_for_template.submit_to_comfyui, config="schnell").
Resumable: skips indices already on disk. Per-image retry for batch robustness.

  python3 -m scripts.publish.waystream_covers.pools --count 15
  python3 -m scripts.publish.waystream_covers.pools --smoke --only tomas_vidal
"""
from __future__ import annotations
import os
import sys
import time
from pathlib import Path

from . import assign as A

COMFY = os.environ.get("COMFYUI_URL", "http://100.92.68.74:8188")


def gen(count=15, only=None, smoke=False):
    os.environ["COMFYUI_URL"] = COMFY
    sys.path.insert(0, str(A.ROOT))
    from scripts.publish.render_imagery_for_template import submit_to_comfyui, ImageryPlan

    cfg = A.load_cfg()
    prompts = cfg["pool"]["prompts"]
    neg = cfg["pool"]["negative"]
    authors = [a for a in cfg["authors"] if cfg["authors"][a]["family"] in cfg["image_families"]]
    if only:
        authors = [a for a in authors if a in only]
    n = 1 if smoke else count
    made = errs = 0
    for aid in authors:
        prompt = prompts.get(aid)
        if not prompt:
            print(f"SKIP {aid}: no pool prompt in config", flush=True)
            continue
        d = A.POOLS / aid
        d.mkdir(parents=True, exist_ok=True)
        for i in range(1, n + 1):
            out = d / f"{i:02d}.png"
            if out.exists() and not smoke:
                continue
            seed = i * 97 + 13
            plan = ImageryPlan(book_id=aid, full_book_id=aid, genre="abstract", width=1024, height=1280,
                               aspect=0.8, positive_prompt=prompt, negative_prompt=neg,
                               output_path=out, type_dominant=False)
            for attempt in range(3):
                try:
                    b = submit_to_comfyui(plan, comfyui_url=COMFY, config="schnell", seed=seed)
                    out.write_bytes(b)
                    made += 1
                    print(f"{aid} {i:02d}/{n} ok ({len(b)//1024}kb)", flush=True)
                    break
                except Exception as e:
                    if attempt == 2:
                        errs += 1
                        print(f"{aid} {i:02d} ERR {e}", flush=True)
                    else:
                        time.sleep(4)
    print(f"POOLS DONE made={made} errs={errs}", flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=15)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    gen(a.count, set(a.only) if a.only else None, a.smoke)
