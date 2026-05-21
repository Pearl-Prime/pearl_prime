"""ToonOut (BiRefNet fine-tuned on anime) cutout backend.

Per docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md §13 (Phase 1 ToonOut fallback).
Source: github.com/MatteoKartoon/BiRefNet  +  hf.co/joelseytre/toonout
License: MIT (code), MIT (weights), CC-BY-4.0 (dataset).
Weights expected at models/cutout/toonout/birefnet_finetuned_toonout.pth
(885 MB; .gitignored). Operator pulls separately from
https://huggingface.co/joelseytre/toonout/resolve/main/birefnet_finetuned_toonout.pth

Tier 1 (operator-present). No LLM calls. Per CLAUDE.md tier policy.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
TOONOUT_CHECKPOINT = REPO / "models" / "cutout" / "toonout" / "birefnet_finetuned_toonout.pth"


@lru_cache(maxsize=1)
def _load_toonout_model():
    """Lazy singleton load (first toonout-archetype panel triggers; subsequent reuse).

    Returns (model, device) tuple.
    """
    import torch
    from transformers import AutoModelForImageSegmentation
    if not TOONOUT_CHECKPOINT.is_file():
        raise FileNotFoundError(
            f"ToonOut weights missing: {TOONOUT_CHECKPOINT}\n"
            f"Download from https://huggingface.co/joelseytre/toonout/resolve/main/birefnet_finetuned_toonout.pth (885 MB .pth)."
        )
    model = AutoModelForImageSegmentation.from_pretrained(
        "ZhengPeng7/BiRefNet", trust_remote_code=True)
    state_dict = torch.load(TOONOUT_CHECKPOINT, map_location="cpu")
    # Strip module._orig_mod. / module. prefixes that may be present
    clean = {}
    for k, v in state_dict.items():
        if k.startswith("module._orig_mod."):
            clean[k[len("module._orig_mod."):]] = v
        elif k.startswith("module."):
            clean[k[len("module."):]] = v
        else:
            clean[k] = v
    model.load_state_dict(clean)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return model.to(device).eval(), device


def toonout_cutout(image: Image.Image) -> Image.Image:
    """RGB PIL.Image → RGBA PIL.Image.

    Output contract identical to rembg.remove(): RGBA at input dims, alpha channel
    contains the subject mask. Downstream V4 validators (§12.3 rembg_clean_alpha,
    character_extraction_coverage, background_bleed_check) operate on the alpha
    channel only — they treat this output the same as rembg output.
    """
    import torch
    from torchvision import transforms
    model, device = _load_toonout_model()
    rgb = image.convert("RGB")
    tx = transforms.Compose([
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    with torch.no_grad():
        pred = model(tx(rgb).unsqueeze(0).to(device))[-1].sigmoid().cpu()
    mask = transforms.ToPILImage()(pred[0].squeeze()).resize(rgb.size)
    out = rgb.copy()
    out.putalpha(mask)
    return out
