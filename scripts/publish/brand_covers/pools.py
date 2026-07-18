"""Market-agnostic FLUX-schnell author image pools for ANY brand.

Generated ONCE per (brand, author); reused across all 14 locales (only composited
text changes per book/locale). schnell only — flux1-dev is BANNED. Pearl Star ComfyUI.

  PYTHONPATH=. python3 -m scripts.publish.brand_covers.pools --brand stillness_press --authors lena_thorne daniel_voss --n 8
  PYTHONPATH=. python3 -m scripts.publish.brand_covers.pools --brand stillness_press --all-image-authors --n 12
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path

os.environ.setdefault("COMFYUI_URL", "http://100.92.68.74:8188")

from scripts.publish.render_imagery_for_template import submit_to_comfyui, ImageryPlan  # noqa: E402
from . import assignment as A  # noqa: E402
from . import adapter as AD  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
NEG = ("text, words, letters, typography, title, watermark, signature, people, "
       "faces, hands, buildings, frame, border, ui, logo")


def prompt_for(card: dict) -> str:
    """Deterministic atmospheric prompt from the author's palette warmth."""
    deep = card["deep"].lstrip("#")
    r, b = int(deep[0:2], 16), int(deep[4:6], 16)
    if r >= b:  # warm
        vibe = ("warm charcoal and soft amber tones, a single luminous arch of light "
                "emerging from shadow, textured paper grain")
    else:       # cool
        vibe = ("deep dusk navy sky over a warm cream lower field, a soft low horizon "
                "line of dawn light, subtle ink-wash texture")
    return ("abstract atmospheric book cover background, " + vibe +
            ", contemplative, minimal, fine-art, no text, no people")


def gen_pool(brand_id: str, author_id: str, n: int, url: str):
    card = A.assign_author(brand_id, author_id)
    if card["family"] not in A.IMAGE_FAMILIES:
        print(f"skip {author_id}: image-free family ({card['family']})")
        return 0
    d = ROOT / f"artifacts/covers/{brand_id}/author_pools/{author_id}"
    d.mkdir(parents=True, exist_ok=True)
    prompt = prompt_for(card)
    ok = 0
    for k in range(1, n + 1):
        out = d / f"{k:02d}.png"
        plan = ImageryPlan(book_id=author_id, full_book_id=author_id, genre="abstract",
                           width=1024, height=1280, aspect=0.8, positive_prompt=prompt,
                           negative_prompt=NEG, output_path=out, type_dominant=False)
        try:
            img = submit_to_comfyui(plan, comfyui_url=url, config="schnell", seed=k * 97 + 13 + A._h(author_id) % 1000)
            out.write_bytes(img)
            ok += 1
            print(f"{author_id} {k}/{n} ok", flush=True)
        except Exception as e:
            print(f"{author_id} {k} ERR {e}", flush=True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--authors", nargs="*", default=[])
    ap.add_argument("--all-image-authors", action="store_true")
    ap.add_argument("--n", type=int, default=8)
    args = ap.parse_args()
    url = os.environ["COMFYUI_URL"]

    authors = list(args.authors)
    if args.all_image_authors:
        rows = AD.rows_for_brand(args.brand)
        for aid in sorted({r["author_id"] for r in rows}):
            if A.assign_author(args.brand, aid)["family"] in A.IMAGE_FAMILIES:
                authors.append(aid)
        authors = sorted(set(authors))
    if not authors:
        print("no authors given (use --authors or --all-image-authors)")
        return
    print(f"pools for {args.brand}: {authors} (n={args.n} each, schnell)")
    total = sum(gen_pool(args.brand, a, args.n, url) for a in authors)
    print(f"POOLS DONE — {total} images", flush=True)


if __name__ == "__main__":
    main()
