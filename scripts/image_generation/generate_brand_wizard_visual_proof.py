#!/usr/bin/env python3
"""
Generate and stage BrandWizard proof images (ComfyUI FLUX) + Tier-1 bank curation.

Usage:
  PYTHONPATH=. COMFYUI_URL=http://192.168.1.112:8188 python3 scripts/image_generation/generate_brand_wizard_visual_proof.py --analyze
  PYTHONPATH=. COMFYUI_URL=... python3 scripts/image_generation/generate_brand_wizard_visual_proof.py --tier1
  PYTHONPATH=. COMFYUI_URL=... python3 scripts/image_generation/generate_brand_wizard_visual_proof.py --generate-all

See brand-wizard-app onboarding proof paths in BrandWizard.jsx.
"""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.video.flux_client import call_comfyui, load_yaml  # noqa: E402

BANK_ROOT = REPO_ROOT / "artifacts" / "video" / "image_banks"
WIZARD_ART = REPO_ROOT / "artifacts" / "video" / "image_banks" / "wizard"
WIZARD_PUB = REPO_ROOT / "brand-wizard-app" / "public" / "onboarding" / "proof" / "wizard"


def _constraints() -> tuple[list[str], list[str]]:
    cfg = load_yaml("config/video/prompt_constraints.yaml")
    return list(cfg.get("no_adoration", [])), list(cfg.get("shared_negatives", []))


def neg_no_face(extra: list[str] | None = None) -> str:
    no_ad, shared = _constraints()
    parts = no_ad + shared + (extra or [])
    return ", ".join(parts)


def neg_with_face(extra: list[str] | None = None) -> str:
    """Same as bank negatives but allow illustrated faces."""
    no_ad, shared = _constraints()
    filtered = [s for s in shared if "no full faces" not in s.lower() and "no faces" not in s.lower()]
    parts = no_ad + filtered + [
        "photorealistic",
        "stock photo",
        "hyperrealistic",
        "DSLR",
        "3D render",
        "anime",
        "manga panels",
    ]
    if extra:
        parts.extend(extra)
    return ", ".join(parts)


def ensure_dirs() -> None:
    WIZARD_ART.mkdir(parents=True, exist_ok=True)
    WIZARD_PUB.mkdir(parents=True, exist_ok=True)


def publish(path: Path) -> None:
    """Copy artifact to public onboarding folder."""
    dest = WIZARD_PUB / path.name
    shutil.copy2(path, dest)


def analyze_bank() -> list[dict]:
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("pip install pillow for --analyze")

    rows = []
    for png in sorted(BANK_ROOT.glob("*/*.png")):
        if "wizard" in png.parts:
            continue
        im = Image.open(png).convert("RGB")
        im.thumbnail((256, 256))
        px = list(im.getdata())
        n = len(px)
        lum = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in px]
        r_m = sum(p[0] for p in px) / n
        g_m = sum(p[1] for p in px) / n
        b_m = sum(p[2] for p in px) / n
        warm = (r_m + g_m * 0.5) - b_m
        rows.append(
            {
                "path": str(png.relative_to(REPO_ROOT)),
                "lum": statistics.mean(lum),
                "std": statistics.pstdev(lum) if n > 1 else 0,
                "warm": warm,
            }
        )
    rows.sort(key=lambda x: x["lum"])
    return rows


def tier1_curate() -> None:
    ensure_dirs()
    rows = analyze_bank()
    by_lum = sorted(rows, key=lambda x: x["lum"])
    darkest = by_lum[0]["path"]
    lightest = by_lum[-1]["path"]
    mid = sorted(rows, key=lambda x: x["warm"], reverse=True)
    warmest = mid[0]["path"]
    contrasty = max(rows, key=lambda x: x["std"])["path"]
    # Premium: lighter + moderate contrast; cosmic: dark + cooler
    cool_dark = sorted([r for r in rows if r["lum"] < 100], key=lambda x: x["warm"])[:3]
    cosmic_pick = cool_dark[0]["path"] if cool_dark else by_lum[len(by_lum) // 4]["path"]
    premium_candidates = sorted([r for r in rows if r["lum"] > 130], key=lambda x: -x["std"])
    premium_pick = premium_candidates[0]["path"] if premium_candidates else by_lum[-3]["path"]
    if premium_pick == contrasty and len(premium_candidates) > 1:
        premium_pick = premium_candidates[1]["path"]
    elif premium_pick == contrasty:
        premium_pick = by_lum[-4]["path"]

    mapping = {
        "style_calm_minimal.png": lightest,
        "style_dark_intense.png": darkest,
        "style_earthy_organic.png": warmest,
        "style_bold_modern.png": contrasty,
        "style_premium_soft.png": premium_pick,
        "style_sacred_cosmic.png": cosmic_pick,
    }
    manifest = {"tier1_visual_styles": {}, "source": "artifacts/video/image_banks curated luminance/warmth"}
    for dest_name, rel in mapping.items():
        src = REPO_ROOT / rel
        out = WIZARD_ART / dest_name
        shutil.copy2(src, out)
        publish(out)
        manifest["tier1_visual_styles"][dest_name] = rel
    (WIZARD_ART / "tier1_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Tier-1 visual styles copied:", json.dumps(manifest["tier1_visual_styles"], indent=2))

    # Topic ambient library (reuse 8 bank files for Step 7 tags)
    topic_pool = [
        by_lum[len(by_lum) * 3 // 4]["path"],
        by_lum[len(by_lum) // 2]["path"],
        warmest,
        by_lum[len(by_lum) // 3]["path"],
        contrasty,
        lightest,
        darkest,
        premium_pick,
    ]
    topic_tags = [
        "anxiety-at-night",
        "overthinking",
        "panic-grounding",
        "sunday-dread",
        "burnout-recovery",
        "nervous-system-reset",
        "decision-fatigue",
        "phone-addiction",
        "grief-timeline",
        "toxic-relationship-healing",
        "intergenerational-trauma",
        "heartbreak-recovery",
        "emotional-numbness",
        "feeling-behind",
        "quarter-life-crisis",
        "identity-rebuild",
        "purpose-after-30",
        "habit-building",
        "ADHD-productivity",
        "dopamine-detox",
        "deep-work",
        "meditation-beginners",
        "meaning-after-loss",
        "spiritual-no-religion",
        "inner-peace-chaos",
        "mindfulness-skeptics",
    ]
    topic_manifest = {}
    for i, tag in enumerate(topic_tags):
        rel = topic_pool[i % len(topic_pool)]
        dest_name = f"topic_{tag.replace('-', '_')}.png"
        src = REPO_ROOT / rel
        out = WIZARD_ART / dest_name
        shutil.copy2(src, out)
        publish(out)
        topic_manifest[tag] = str(Path(rel).as_posix())
    (WIZARD_ART / "tier1_topics_manifest.json").write_text(json.dumps(topic_manifest, indent=2), encoding="utf-8")
    print("Tier-1 topic images:", len(topic_manifest))


def gen_one(name: str, prompt: str, negative: str, width: int, height: int, seed: int) -> Path:
    url = __import__("os").environ.get("COMFYUI_URL", "").strip()
    if not url:
        raise SystemExit("Set COMFYUI_URL")
    ensure_dirs()
    out = WIZARD_ART / name
    if out.exists() and out.stat().st_size > 1000:
        print("skip existing", name)
        publish(out)
        return out
    print("generate", name, flush=True)
    data = call_comfyui(url, prompt, negative, width=width, height=height, seed=seed)
    out.write_bytes(data)
    publish(out)
    return out


ARCHETYPE_JOBS = [
    ("archetype_stillness_01.png", "nervous_system", 910001),
    ("archetype_stillness_02.png", "nervous_system", 910002),
    ("archetype_stillness_03.png", "nervous_system", 910003),
    ("archetype_compass_01.png", "identity_direction", 910011),
    ("archetype_compass_02.png", "identity_direction", 910012),
    ("archetype_compass_03.png", "identity_direction", 910013),
    ("archetype_lantern_01.png", "emotional_healing", 910021),
    ("archetype_lantern_02.png", "emotional_healing", 910022),
    ("archetype_lantern_03.png", "emotional_healing", 910023),
    ("archetype_clear_mind_01.png", "performance_focus", 910031),
    ("archetype_clear_mind_02.png", "performance_focus", 910032),
    ("archetype_clear_mind_03.png", "performance_focus", 910033),
    ("archetype_phoenix_01.png", "spiritual_awakening", 910041),
    ("archetype_phoenix_02.png", "spiritual_awakening", 910042),
    ("archetype_phoenix_03.png", "spiritual_awakening", 910043),
]

ARCHETYPE_PROMPTS = {
    "nervous_system": (
        "Vast empty white gallery wall, single delicate indigo ink brushstroke like breath, soft lavender mist at floor, "
        "zen spaciousness, gouache illustration, paper grain, no people, no faces, dramatic negative space, calm somatic mood"
    ),
    "identity_direction": (
        "Open coastal horizon at dawn, emerald teal sky gradient, faint compass rose etched in wet sand, path of footprints "
        "leading forward, hopeful directional light, gouache illustration, no people, no faces, generous sky"
    ),
    "emotional_healing": (
        "Rain-streaked window at night, warm rose pink bokeh lights outside, soft watercolor paper texture, empty chair with folded blanket, "
        "intimate healing mood, gouache, no people, no faces"
    ),
    "performance_focus": (
        "Bold amber and orange geometric planes, sharp diagonal light beams, kinetic energy lines, crisp contrast, "
        "abstract focus laboratory, gouache with hard edges, no people, no faces, energetic"
    ),
    "spiritual_awakening": (
        "Deep violet cosmic gradient, subtle sacred geometry outline, thin gold foil accent line, contemplative depth, "
        "stars barely visible, gouache illustration, no people, no faces, mystical but calm"
    ),
}

MOMENT_JOBS = [
    ("moment_2am_overthinking.png", 920001, "Dark bedroom at night, phone screen glow on nightstand, rumpled sheets, city light through blinds, moody blue shadows, empty room, no people, no faces, gouache illustration, cinematic loneliness"),
    ("moment_after_breakup.png", 920002, "Empty apartment living room, moving boxes, single mug on table, grey afternoon light, silence and absence, warm neutrals drained, gouache, no people, no faces"),
    ("moment_burnout_office.png", 920003, "Fluorescent office bathroom mirror, harsh overhead light, paper towels, exhaustion atmosphere, cool grey tiles, no people visible, no faces, gouache illustration"),
    ("moment_comparison_scroll.png", 920004, "Smartphone on desk glowing with endless feed tiles, abstract social icons, overwhelming colorful UI reflection, person not shown, no faces, gouache, slight motion blur on screen only"),
    ("moment_panic_tight_space.png", 920005, "Claustrophobic narrow corridor closing in, walls leaning, desaturated cold palette, tight composition, no people, no faces, anxiety mood, gouache"),
    ("moment_sunday_dread.png", 920006, "Sunday afternoon couch, wall clock prominent, dim living room, sinking heavy light, tea gone cold on table, no people, no faces, anticipatory gloom, gouache illustration"),
]

PERSONA_JOBS = [
    ("persona_burned_out_pro.png", 930001, "Upper body gouache watercolor illustration, South Asian woman in business blazer, head in hands at desk, warm office lamp light, dignified exhaustion, therapeutic art style, generous negative space, soft edges, not photorealistic"),
    ("persona_gen_z_seeker.png", 930002, "Upper body gouache illustration, Black young adult holding smartphone, uncertain worried expression, colorful chaotic abstract shapes behind, not anime, not photorealistic, warm therapeutic palette"),
    ("persona_gen_alpha.png", 930003, "Upper body gouache illustration, East Asian child about 11, wide curious eyes, nature leaves and subtle digital grid motifs around, gentle wonder, not anime, illustrative"),
    ("persona_grief_carrier.png", 930004, "Upper body gouache illustration, Middle Eastern man holding lit candle, soft warm light on face, gentle sadness, compassionate eyes, not melodramatic, dark rose and amber tones"),
    ("persona_anxious_achiever.png", 930005, "Upper body gouache illustration, Latina woman in crisp blouse, polished smile strained, eyes show worry, modern office soft background, high achiever mask slipping, illustrative"),
    ("persona_spiritual_returner.png", 930006, "Upper body gouache illustration, white older man meditating eyes half open, skeptical but soft expression, simple beige room, contemplative, warm light"),
    ("persona_overwhelmed_parent.png", 930007, "Upper body gouache illustration, Black mother holding small stuffed toy, tired loving eyes, cozy messy living room warm tones, compassionate domestic scene"),
]

EMOTION_JOBS = [
    ("emotion_finally_calm.png", 940001, "512 square gouache badge, face eyes closed slight smile, soft blue wash, simple composition, therapeutic illustration"),
    ("emotion_safe_in_body.png", 940002, "512 square gouache, hands on chest self-hug, warm amber glow, no full scene"),
    ("emotion_clear_headed.png", 940003, "512 square gouache, face forward bright attentive eyes, clean white background, clarity"),
    ("emotion_in_control.png", 940004, "512 square gouache, hands on steering wheel from chest up, confident posture, cropped"),
    ("emotion_permission_rest.png", 940005, "512 square gouache, person curled in blanket from above, peaceful, warm tones"),
    ("emotion_energized.png", 940006, "512 square gouache, figure stretching arms up sunrise colors, energetic movement"),
    ("emotion_connected_purpose.png", 940007, "512 square gouache, silhouette toward horizon warm compass-light sky"),
    ("emotion_released.png", 940008, "512 square gouache, figure arms open wind light breaking through"),
    ("emotion_less_alone.png", 940009, "512 square gouache, two seated silhouettes side by side warm shared lamp light"),
    ("emotion_forgiven.png", 940010, "512 square gouache, hands opening releasing paper birds into light"),
    ("emotion_grounded.png", 940011, "512 square gouache, bare feet on grass and soil close-up"),
    ("emotion_hopeful.png", 940012, "512 square gouache, face turning toward warm sunrise side light"),
    ("emotion_present.png", 940013, "512 square gouache, extreme close-up calm focused eyes"),
    ("emotion_confident.png", 940014, "512 square gouache, upper body standing tall shoulders back warm spotlight"),
    ("emotion_resilient.png", 940015, "512 square gouache, person standing in gentle rain calm expression eyes open"),
]


def copy_hero_archetypes() -> None:
    """Stable filenames for JSX map to first variant of each archetype world."""
    pairs = [
        ("archetype_nervous_system.png", "archetype_stillness_01.png"),
        ("archetype_identity_direction.png", "archetype_compass_01.png"),
        ("archetype_emotional_healing.png", "archetype_lantern_01.png"),
        ("archetype_performance_focus.png", "archetype_clear_mind_01.png"),
        ("archetype_spiritual_awakening.png", "archetype_phoenix_01.png"),
    ]
    for alias, target in pairs:
        t = WIZARD_ART / target
        if not t.exists():
            continue
        shutil.copy2(t, WIZARD_ART / alias)
        shutil.copy2(t, WIZARD_PUB / alias)


def generate_all() -> None:
    neg_nf = neg_no_face()
    neg_f = neg_with_face()
    for fname, key, seed in ARCHETYPE_JOBS:
        gen_one(fname, ARCHETYPE_PROMPTS[key], neg_nf, 1024, 576, seed)
    for fname, seed, prompt in MOMENT_JOBS:
        gen_one(fname, prompt, neg_nf, 1024, 576, seed)
    for fname, seed, prompt in PERSONA_JOBS:
        gen_one(fname, prompt, neg_f, 1024, 576, seed)
    for fname, seed, prompt in EMOTION_JOBS:
        gen_one(fname, prompt, neg_f, 512, 512, seed)
    copy_hero_archetypes()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--tier1", action="store_true")
    ap.add_argument("--generate-all", action="store_true")
    args = ap.parse_args()
    if args.analyze:
        rows = analyze_bank()
        print(json.dumps(rows[:8], indent=2))
        print("...")
        print(json.dumps(rows[-8:], indent=2))
        return
    if args.tier1:
        tier1_curate()
        return
    if args.generate_all:
        generate_all()
        return
    ap.print_help()


if __name__ == "__main__":
    main()
