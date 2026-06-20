import os, sys
from pathlib import Path
sys.path.insert(0,"/Users/ahjan/phoenix_omega")
os.environ["COMFYUI_URL"]="http://100.92.68.74:8188"
from scripts.publish.render_imagery_for_template import submit_to_comfyui, ImageryPlan
AUTHORS={
 "lena_frost":"abstract atmospheric book cover background, deep dusk navy sky over a warm cream lower field, a soft low horizon line of dawn light, subtle ink-wash texture, contemplative, minimal, fine-art, no text, no words, no people, no buildings",
 "theo_castellan":"abstract atmospheric book cover background, warm charcoal and soft amber tones, a single luminous arch of light emerging from shadow, textured paper grain, grounded, contemplative, minimal, fine-art, no text, no words, no people, no buildings",
}
NEG="text, words, letters, typography, title, watermark, signature, people, faces, hands, buildings, frame, border, ui, logo"
N=8
for aid,prompt in AUTHORS.items():
    d=Path(f"/Users/ahjan/phoenix_omega/artifacts/waystream/author_pools/{aid}"); d.mkdir(parents=True,exist_ok=True)
    for i in range(1,N+1):
        plan=ImageryPlan(book_id=aid,full_book_id=aid,genre="abstract",width=1024,height=1280,aspect=0.8,
            positive_prompt=prompt,negative_prompt=NEG,output_path=d/f"{i:02d}.png",type_dominant=False)
        try:
            b=submit_to_comfyui(plan,comfyui_url=os.environ["COMFYUI_URL"],config="schnell",seed=i*97+13)
            open(d/f"{i:02d}.png","wb").write(b); print(f"{aid} {i}/{N} ok",flush=True)
        except Exception as e: print(f"{aid} {i} ERR {e}",flush=True)
print("POOLS DONE",flush=True)
