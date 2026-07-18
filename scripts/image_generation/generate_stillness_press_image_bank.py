#!/usr/bin/env python3
"""Generate complete Stillness Press (US Brand 1) manga image bank.

Targets Pearl Star local ComfyUI (RTX 3060) at http://192.168.1.112:8188.
Generates all character views, expressions, backgrounds, panel types, props,
motifs, and anchor panels needed to produce any manga book in this brand.

Usage:
  python3 scripts/image_generation/generate_stillness_press_image_bank.py \
    --category all \
    --out artifacts/manga/image_bank/stillness_press/ \
    --comfyui-url http://192.168.1.112:8188 \
    --workers 2 \
    --progress artifacts/manga/image_bank/stillness_press/GENERATION_PROGRESS.tsv

Categories: model_sheets, expressions, poses, locations, atmospheric,
            covers, chapter_openers, silence, props, motifs, anchors,
            registry, all
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required — pip install pyyaml", file=sys.stderr)
    sys.exit(1)

from scripts.image_generation.image_qc import run_panel_qc

# ── Paths ──
BRAND_STYLES_PATH = REPO_ROOT / "config" / "manga" / "brand_illustration_styles.yaml"
TEACHER_PROMPTS_PATH = REPO_ROOT / "config" / "manga" / "teacher_character_prompts.yaml"
WORKFLOW_TXT2IMG = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_txt2img_manga.json"
WORKFLOW_IP_ADAPTER = REPO_ROOT / "scripts" / "image_generation" / "comfyui_workflows" / "flux_ip_adapter_manga.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "manga" / "image_bank" / "stillness_press"

# ── Brand constants ──
BRAND_ID = "stillness_press"
LOCALE = "en_US"
CHARACTER_ID = "ahjan"

# ── Prompt templates (from brand_illustration_styles.yaml) ──
BASE_POSITIVE = (
    "seinen manga, soft ink linework, warm earth-toned watercolor wash, "
    "contemplative mood, generous negative space, paper texture grain, "
    "Studio Ghibli meets Vagabond"
)

BASE_NEGATIVE = (
    "bright neon, harsh shadows, action lines, speed effects, chibi, "
    "exaggerated expressions, battle aura, dark horror, photorealistic, "
    "3D render, western comic, deformed hands, extra fingers, watermark, "
    "text, signature"
)

# Ahjan character prompt core (from teacher_character_prompts.yaml)
AHJAN_CHARACTER_BASE = (
    "seinen manga character, soft ink linework, warm earth-toned watercolor wash, "
    "gentle eyes with depth and stillness, monastic simplicity, simple robes or "
    "clean modern clothing, calm present expression quietly radiating warmth, "
    "subtle golden light aura, high detail face, clean linework"
)

# Token budget limits (per Visual Agent Spec)
MAX_POSITIVE_TOKENS = 120
MAX_NEGATIVE_TOKENS = 60

# ── Dimension presets ──
DIM_PORTRAIT = (768, 1152)      # Portrait panels
DIM_SQUARE = (1024, 1024)       # Standard square
DIM_LANDSCAPE = (1280, 720)     # Backgrounds / chapter openers
DIM_WIDE = (1280, 720)          # Wide cinematic
DIM_DETAIL = (1024, 1024)       # Detail shots
DIM_COVER = (768, 1152)         # Cover panels (portrait 2:3)

MAX_RETRIES = 3


# ═══════════════════════════════════════════════════════════════════
# ComfyUI local API client
# ═══════════════════════════════════════════════════════════════════

class ComfyUIClient:
    """Minimal client for local ComfyUI HTTP API."""

    def __init__(self, base_url: str = "http://192.168.1.112:8188"):
        self.base_url = base_url.rstrip("/")

    def _request(self, path: str, data: bytes | None = None, method: str = "GET") -> Any:
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, data=data, method=method)
        if data:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=600) as resp:
            return json.loads(resp.read())

    def check_health(self) -> dict[str, Any]:
        """Verify ComfyUI is reachable."""
        return self._request("/system_stats")

    def queue_prompt(self, workflow: dict[str, Any], *, client_id: str = "") -> str:
        """Submit a workflow to the queue. Returns prompt_id."""
        # Strip _meta key — ComfyUI API rejects unknown node types
        clean_wf = {k: v for k, v in workflow.items() if k != "_meta"}
        payload = {"prompt": clean_wf}
        if client_id:
            payload["client_id"] = client_id
        result = self._request("/prompt", json.dumps(payload).encode(), method="POST")
        return result["prompt_id"]

    def get_history(self, prompt_id: str) -> dict[str, Any]:
        """Get execution history for a prompt."""
        return self._request(f"/history/{prompt_id}")

    def poll_completion(self, prompt_id: str, max_wait: float = 300.0) -> dict[str, Any]:
        """Poll until prompt completes or times out."""
        start = time.time()
        while time.time() - start < max_wait:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id]
            time.sleep(2.0)
        raise TimeoutError(f"Prompt {prompt_id} did not complete within {max_wait}s")

    def download_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Download a generated image from ComfyUI."""
        params = f"?filename={filename}&subfolder={subfolder}&type={folder_type}"
        url = f"{self.base_url}/view{params}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()


# ═══════════════════════════════════════════════════════════════════
# Workflow builder
# ═══════════════════════════════════════════════════════════════════

def load_workflow(path: Path) -> dict[str, Any]:
    """Load a ComfyUI workflow JSON template."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_workflow(
    template: dict[str, Any],
    *,
    positive_prompt: str,
    negative_prompt: str,
    seed: int = 42,
    width: int = 1024,
    height: int = 1024,
) -> dict[str, Any]:
    """Build workflow with prompt/seed/dimension substitutions."""
    workflow = json.loads(json.dumps(template))  # deep copy

    for node_id, node in workflow.items():
        if node_id == "_meta":
            continue
        inputs = node.get("inputs", {})

        # Replace text prompts
        if isinstance(inputs.get("text"), str):
            if "{{positive_prompt}}" in inputs["text"]:
                inputs["text"] = positive_prompt
            elif "{{negative_prompt}}" in inputs["text"]:
                inputs["text"] = negative_prompt

        # Replace seed
        if "seed" in inputs:
            inputs["seed"] = seed
        if "noise_seed" in inputs:
            inputs["noise_seed"] = seed

        # Replace dimensions on EmptyLatentImage
        class_type = node.get("class_type", "")
        if class_type == "EmptyLatentImage":
            inputs["width"] = width
            inputs["height"] = height

    return workflow


# ═══════════════════════════════════════════════════════════════════
# Token budget validation
# ═══════════════════════════════════════════════════════════════════

def count_tokens(text: str) -> int:
    """Estimate token count (word-split approximation)."""
    return len(text.split())


def validate_token_budget(positive: str, negative: str) -> tuple[bool, str]:
    """Check token budget. Returns (passed, detail)."""
    pos_count = count_tokens(positive)
    neg_count = count_tokens(negative)
    issues = []
    if pos_count > MAX_POSITIVE_TOKENS:
        issues.append(f"positive={pos_count}/{MAX_POSITIVE_TOKENS}")
    if neg_count > MAX_NEGATIVE_TOKENS:
        issues.append(f"negative={neg_count}/{MAX_NEGATIVE_TOKENS}")
    if issues:
        return False, f"OVER BUDGET: {', '.join(issues)}"
    return True, f"OK: positive={pos_count}, negative={neg_count}"


# ═══════════════════════════════════════════════════════════════════
# Deterministic seed from asset_id
# ═══════════════════════════════════════════════════════════════════

def seed_from_id(asset_id: str) -> int:
    """Deterministic seed: hash(asset_id) % 2^32."""
    return int(hashlib.sha256(asset_id.encode()).hexdigest(), 16) % (2**32)


# ═══════════════════════════════════════════════════════════════════
# Progress tracker
# ═══════════════════════════════════════════════════════════════════

class ProgressTracker:
    """Track generation progress in a TSV file."""

    HEADER = "asset_id\tcategory\tstatus\tpath\tseed\tgenerated_at\n"

    def __init__(self, path: Path):
        self.path = path
        self.completed: set[str] = set()
        self._load()

    def _load(self):
        if self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines()[1:]:  # skip header
                parts = line.split("\t")
                if len(parts) >= 3 and parts[2] in ("completed", "passed"):
                    self.completed.add(parts[0])

    def is_done(self, asset_id: str) -> bool:
        return asset_id in self.completed

    def record(self, asset_id: str, category: str, status: str, path: str, seed: int):
        now = datetime.now(timezone.utc).isoformat()
        if not self.path.is_file():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(self.HEADER, encoding="utf-8")
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"{asset_id}\t{category}\t{status}\t{path}\t{seed}\t{now}\n")
        if status in ("completed", "passed"):
            self.completed.add(asset_id)


class FailureTracker:
    """Track generation failures in a TSV file."""

    HEADER = "asset_id\tcategory\tattempts\tlast_error\ttimestamp\n"

    def __init__(self, path: Path):
        self.path = path

    def record(self, asset_id: str, category: str, attempts: int, error: str):
        now = datetime.now(timezone.utc).isoformat()
        if not self.path.is_file():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(self.HEADER, encoding="utf-8")
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"{asset_id}\t{category}\t{attempts}\t{error}\t{now}\n")


# ═══════════════════════════════════════════════════════════════════
# Image bank definitions — all 11 categories
# ═══════════════════════════════════════════════════════════════════

def _character_prompt(subject: str) -> str:
    """Build character-specific positive prompt."""
    return f"{AHJAN_CHARACTER_BASE}, {subject}"


def _scene_prompt(subject: str) -> str:
    """Build scene/background positive prompt."""
    return f"{BASE_POSITIVE}, {subject}"


def get_model_sheets() -> list[dict[str, Any]]:
    """Category 1: Character model sheets (12 images)."""
    items = [
        ("ahjan_front_neutral", "facing forward, neutral calm expression", "full body, center frame", DIM_PORTRAIT),
        ("ahjan_front_speaking", "facing forward, gentle speaking expression, slight warmth", "bust shot", DIM_PORTRAIT),
        ("ahjan_3quarter_left", "3/4 view facing left", "full body", DIM_PORTRAIT),
        ("ahjan_3quarter_right", "3/4 view facing right", "full body", DIM_PORTRAIT),
        ("ahjan_profile_left", "side profile facing left", "full body", DIM_PORTRAIT),
        ("ahjan_profile_right", "side profile facing right", "full body", DIM_PORTRAIT),
        ("ahjan_seated_meditation", "seated cross-legged, eyes closed, meditative stillness", "full body", DIM_PORTRAIT),
        ("ahjan_seated_teaching", "seated, gentle hand gesture, teaching pose", "full body", DIM_PORTRAIT),
        ("ahjan_walking", "walking slowly, forest path implied", "full body", DIM_PORTRAIT),
        ("ahjan_bowing", "gentle bow, respectful, humble", "full body", DIM_PORTRAIT),
        ("ahjan_hands_detail", "close-up of hands in mudra or resting", "hands only, high detail", DIM_DETAIL),
        ("ahjan_face_detail", "face close-up, eyes open with gentle depth", "face only, high detail", DIM_DETAIL),
    ]
    return [
        {
            "asset_id": aid,
            "category": "model_sheets",
            "positive": _character_prompt(f"{subj}, {cam}"),
            "negative": BASE_NEGATIVE,
            "path": f"character/ahjan/model_sheets/{aid}.png",
            "dimensions": dims,
        }
        for aid, subj, cam, dims in items
    ]


def get_expressions() -> list[dict[str, Any]]:
    """Category 2: Expression range (8 images)."""
    items = [
        ("calm", "serene, present, at rest"),
        ("compassion", "warm concern, gentle sorrow for another's pain"),
        ("insight", "quiet recognition, understanding dawning"),
        ("questioning", "gentle curiosity, soft inward reflection"),
        ("warmth", "open warmth, welcoming, slight smile"),
        ("stillness", "eyes half-closed, deep inner quiet"),
        ("surprise_gentle", "mild gentle surprise, eyebrows slightly raised"),
        ("grief_compassion", "holding sadness with dignity, not collapsed"),
    ]
    return [
        {
            "asset_id": f"ahjan_expr_{name}",
            "category": "expressions",
            "positive": _character_prompt(f"{desc}, bust shot, same lighting, same clothing"),
            "negative": BASE_NEGATIVE,
            "path": f"character/ahjan/expressions/ahjan_expr_{name}.png",
            "dimensions": DIM_PORTRAIT,
        }
        for name, desc in items
    ]


def get_poses() -> list[dict[str, Any]]:
    """Category 3: Pose library (16 images)."""
    items = [
        ("standing_open", "standing, arms at sides, open body language", "teaching scene"),
        ("standing_gesturing", "one hand raised gently, teaching gesture", "explanation panel"),
        ("standing_listening", "hands clasped, patient listening", "dialogue panel"),
        ("walking_path", "walking on path, looking ahead", "transition panel"),
        ("seated_lotus", "lotus position, eyes closed", "meditation panel"),
        ("seated_zazen", "zazen seated, back straight, hands in mudra", "practice panel"),
        ("seated_chair_teaching", "seated on simple chair, leaning slightly forward", "teaching panel"),
        ("kneeling_garden", "kneeling in garden, tending plants", "scene panel"),
        ("standing_window", "standing at window, looking out, back partially to viewer", "reflection panel"),
        ("bow_greeting", "gentle bow, palms together", "opening panel"),
        ("hands_tea", "holding tea bowl with both hands", "intimate panel"),
        ("reading_scroll", "seated, holding scroll or book", "study panel"),
        ("outdoors_looking", "standing outdoors, looking at sky or nature", "wide shot panel"),
        ("silhouette_path", "full silhouette on forest path, back to viewer", "cinematic panel"),
        ("close_listening", "leaning in slightly, listening intently", "intimate dialogue"),
        ("resting_tree", "leaning against tree, eyes closed, peaceful", "contemplative"),
    ]
    return [
        {
            "asset_id": f"ahjan_pose_{name}",
            "category": "poses",
            "positive": _character_prompt(f"{desc}, {ctx}"),
            "negative": BASE_NEGATIVE,
            "path": f"character/ahjan/poses/ahjan_pose_{name}.png",
            "dimensions": DIM_PORTRAIT,
        }
        for name, desc, ctx in items
    ]


def get_locations() -> list[dict[str, Any]]:
    """Category 4: Location backgrounds (18 images)."""
    items = [
        ("loc_meditation_hall", "simple meditation hall, wooden floor, paper screens filtering soft light, cushions arranged, incense smoke curl", "quiet, reverent"),
        ("loc_temple_garden", "Japanese-style garden, raked gravel, mossy stone, single lantern, early morning mist", "contemplative"),
        ("loc_forest_path", "narrow forest path, dappled light through canopy, soft green-gold", "Mushishi-like stillness"),
        ("loc_forest_clearing", "small forest clearing, soft light shaft from above, wildflowers", "spacious, open"),
        ("loc_riverside", "quiet riverbank, smooth stones, reflections, soft water sounds implied", "calming"),
        ("loc_hermitage_interior", "simple hermitage room, wooden walls, single window, scroll on wall, tea bowl", "monastic simplicity"),
        ("loc_hermitage_exterior", "small hermitage among trees, smoke from chimney, path to door", "refuge"),
        ("loc_rooftop_city", "rooftop at dusk, city lights below, sky above, bench", "urban contemplative"),
        ("loc_library_small", "small personal library, low shelves, reading lamp, zafu cushion", "studious peace"),
        ("loc_open_field", "open field at golden hour, tall grass, distant treeline", "spacious, free"),
        ("loc_mountain_path", "winding mountain path, clouds below, pine trees", "perspective, scale"),
        ("loc_tearoom", "traditional tearoom, tokonoma with scroll, tatami, bamboo window", "intimate, refined"),
        ("loc_water_reflection", "still water surface reflecting sky, reeds at edge", "mirror, stillness"),
        ("loc_corridor_light", "long corridor, light at end, simple wooden architecture", "journey, direction"),
        ("loc_garden_bench", "garden bench under maple tree, fallen leaves, afternoon light", "rest, acceptance"),
        ("loc_winter_room", "simple room, snow falling outside window, single candle lit", "warmth within cold"),
        ("loc_dawn_temple_steps", "temple steps at dawn, first light, mist at base", "beginning, threshold"),
        ("loc_empty_dojo", "empty practice space, polished wooden floor, no furniture", "potentiality"),
    ]
    return [
        {
            "asset_id": aid,
            "category": "locations",
            "positive": _scene_prompt(f"{desc}, {mood}, no characters, atmospheric, spacious"),
            "negative": BASE_NEGATIVE,
            "path": f"backgrounds/locations/location_{aid}.png",
            "dimensions": DIM_LANDSCAPE,
        }
        for aid, desc, mood in items
    ]


def get_atmospheric() -> list[dict[str, Any]]:
    """Category 5: Atmospheric backgrounds (8 images)."""
    items = [
        ("warm_mist_gold", "warm golden mist, soft gradient, no defined elements"),
        ("deep_forest_green", "deep forest green atmospheric wash, soft bokeh"),
        ("cool_slate_rain", "cool slate tones, implied rain, diffuse light"),
        ("parchment_blank", "warm parchment texture, clean, for text-heavy panels"),
        ("dawn_orange_horizon", "soft orange-pink dawn horizon, abstract"),
        ("night_indigo_stars", "deep indigo night sky, soft star points, calming"),
        ("autumn_amber", "warm amber and burnt orange wash, leaf-fall implied"),
        ("soft_white_breath", "near-white, soft breathable space, pure stillness"),
    ]
    return [
        {
            "asset_id": f"atm_{name}",
            "category": "atmospheric",
            "positive": _scene_prompt(f"{desc}, abstract, no characters, no objects"),
            "negative": BASE_NEGATIVE,
            "path": f"backgrounds/atmospheric/atm_{name}.png",
            "dimensions": DIM_LANDSCAPE,
        }
        for name, desc in items
    ]


def get_covers() -> list[dict[str, Any]]:
    """Category 6: Cover panels (4 images)."""
    items = [
        ("cover_forest_figure", "Ahjan silhouette on forest path, back to viewer, warm gold light ahead, title space at top"),
        ("cover_meditation_bell", "single bell silhouette, misty background, generous negative space"),
        ("cover_seated_window", "Ahjan seated by window, soft light, seen from behind, landscape outside"),
        ("cover_path_alone", "empty forest path, no character, inviting the viewer in, early morning light"),
    ]
    return [
        {
            "asset_id": name,
            "category": "covers",
            "positive": _scene_prompt(f"{desc}, muted slate-to-white gradient, warm gold accent, contemplative"),
            "negative": BASE_NEGATIVE,
            "path": f"panels/covers/{name}.png",
            "dimensions": DIM_COVER,
        }
        for name, desc in items
    ]


def get_chapter_openers() -> list[dict[str, Any]]:
    """Category 7: Chapter opener panels (6 images)."""
    items = [
        ("opener_dawn_temple", "dawn breaking over temple roofline, birds, mist"),
        ("opener_meditation_hall_empty", "empty meditation hall, morning light through screens, cushions waiting"),
        ("opener_forest_wide", "wide forest establishing shot, Ahjan small figure in distance on path"),
        ("opener_seasons_autumn", "autumn temple garden, fallen leaves on stone, stillness"),
        ("opener_city_rooftop_night", "urban rooftop at night, distant city lights, single figure looking out"),
        ("opener_river_dawn", "river at dawn, mist on water, sense of beginning"),
    ]
    return [
        {
            "asset_id": name,
            "category": "chapter_openers",
            "positive": _scene_prompt(f"{desc}, wide cinematic establishing shot"),
            "negative": BASE_NEGATIVE,
            "path": f"panels/chapter_openers/{name}.png",
            "dimensions": DIM_WIDE,
        }
        for name, desc in items
    ]


def get_silence() -> list[dict[str, Any]]:
    """Category 8: Silence panels (8 images)."""
    items = [
        ("silence_breath", "close-up of hands resting in lap, barely perceptible movement", "pause, breath"),
        ("silence_listening", "ear and profile, eyes closed, listening", "receiving"),
        ("silence_space", "empty cushion in meditation hall, morning light", "absence, waiting"),
        ("silence_tea_steam", "tea bowl, steam rising, hands barely visible", "present moment"),
        ("silence_path_diverge", "forest path splitting, no figure", "choice, threshold"),
        ("silence_water_still", "still water reflection, moment before ripple", "before, potential"),
        ("silence_light_change", "light shifting on wooden floor, no figure", "time passing"),
        ("silence_bell_aftermath", "bell in frame, air vibrating implied, no figure", "resonance"),
    ]
    return [
        {
            "asset_id": name,
            "category": "silence",
            "positive": _scene_prompt(f"{desc}, {func}, wordless, high emotional charge"),
            "negative": BASE_NEGATIVE,
            "path": f"panels/silence/{name}.png",
            "dimensions": DIM_SQUARE,
        }
        for name, desc, func in items
    ]


def get_props() -> list[dict[str, Any]]:
    """Category 9: Props library (12 images)."""
    items = [
        ("prop_tea_bowl", "ceramic tea bowl, warm earth tones, simple"),
        ("prop_bell", "small meditation bell and striker, wood and bronze"),
        ("prop_incense", "incense stick in holder, thin smoke curl"),
        ("prop_scroll", "rolled scroll with ribbon, natural paper color"),
        ("prop_cushion_zafu", "black zafu meditation cushion"),
        ("prop_lantern_stone", "simple stone lantern, unlit"),
        ("prop_lantern_paper", "paper lantern, soft warm glow"),
        ("prop_walking_staff", "simple wooden walking staff"),
        ("prop_book_open", "open book with handwritten text implied"),
        ("prop_stone_path", "stepping stones, garden moss between"),
        ("prop_water_bowl", "stone water bowl, still water surface"),
        ("prop_maple_leaf", "single fallen maple leaf, autumn red"),
    ]
    return [
        {
            "asset_id": name,
            "category": "props",
            "positive": _scene_prompt(f"{desc}, on surface, warm parchment background, clean, no character"),
            "negative": BASE_NEGATIVE,
            "path": f"props/{name}.png",
            "dimensions": DIM_SQUARE,
        }
        for name, desc in items
    ]


def get_motifs() -> list[dict[str, Any]]:
    """Category 10: Motif evolution (6 motifs × 3 stages = 18 images)."""
    motifs = {
        "motif_bell": [
            "bell in deep shadow, barely visible, obscured",
            "bell half in light, emerging from shadow",
            "bell clear, ringing, fully visible, resonant",
        ],
        "motif_path": [
            "path obscured by thick fog, barely visible",
            "path partially visible through thinning mist",
            "open clear path, sunlit, inviting",
        ],
        "motif_light": [
            "single candle in darkness, small flame",
            "candle with spreading warmth, golden glow expanding",
            "dawn light flooding in through window, warm",
        ],
        "motif_water": [
            "turbulent water surface, ripples, agitated",
            "water settling, ripples fading, calming",
            "still mirror surface, perfect reflection, peace",
        ],
        "motif_tree": [
            "bare tree in winter, stark branches, dormant",
            "tree budding in spring, first green leaves",
            "tree in full leaf, lush canopy, alive",
        ],
        "motif_hands": [
            "hands clenched, tense, tight fists",
            "hands loosening, fingers uncurling, releasing",
            "hands open, palms up, receiving, relaxed",
        ],
    }
    items = []
    for motif_id, stages in motifs.items():
        for stage_num, stage_desc in enumerate(stages, 1):
            items.append({
                "asset_id": f"{motif_id}_stage_{stage_num}",
                "category": "motifs",
                "positive": _scene_prompt(f"{stage_desc}, symbolic, contemplative"),
                "negative": BASE_NEGATIVE,
                "path": f"motifs/{motif_id}/stage_{stage_num}.png",
                "dimensions": DIM_SQUARE,
            })
    return items


def get_anchors() -> list[dict[str, Any]]:
    """Category 11: Anchor panels (6 images)."""
    items = [
        ("anchor_01_face_neutral", "Ahjan face, neutral calm, high detail, front view", "close_up_face"),
        ("anchor_02_full_body_standing", "Ahjan standing, full body, front 3/4 view", "dialogue_standard"),
        ("anchor_03_seated_meditation", "Ahjan seated lotus, eyes closed, meditative", "silent_stillness"),
        ("anchor_04_teaching_gesture", "Ahjan with teaching hand gesture, warm expression", "dialogue_standard"),
        ("anchor_05_silhouette", "Ahjan silhouette on path, back to viewer, cinematic", "establishing_shot"),
        ("anchor_06_expression_compassion", "Ahjan expression: compassion, warm concern, bust shot", "emotional_peak"),
    ]
    return [
        {
            "asset_id": name,
            "category": "anchors",
            "positive": _character_prompt(desc),
            "negative": BASE_NEGATIVE,
            "path": f"anchor_panels/{name}.png",
            "dimensions": DIM_PORTRAIT,
            "anchor_category": cat,
        }
        for name, desc, cat in items
    ]


# ═══════════════════════════════════════════════════════════════════
# Category router
# ═══════════════════════════════════════════════════════════════════

CATEGORY_MAP = {
    "model_sheets": get_model_sheets,
    "expressions": get_expressions,
    "poses": get_poses,
    "locations": get_locations,
    "atmospheric": get_atmospheric,
    "covers": get_covers,
    "chapter_openers": get_chapter_openers,
    "silence": get_silence,
    "props": get_props,
    "motifs": get_motifs,
    "anchors": get_anchors,
}

ALL_CATEGORIES = list(CATEGORY_MAP.keys())


# ═══════════════════════════════════════════════════════════════════
# Generation engine
# ═══════════════════════════════════════════════════════════════════

def generate_single(
    client: ComfyUIClient,
    item: dict[str, Any],
    output_dir: Path,
    workflow_template: dict[str, Any],
    *,
    progress: ProgressTracker,
    failures: FailureTracker,
    resume: bool = True,
) -> dict[str, Any]:
    """Generate a single image. Returns result dict."""
    asset_id = item["asset_id"]
    category = item["category"]
    out_path = output_dir / item["path"]

    # Resume check
    if resume and progress.is_done(asset_id):
        print(f"  [SKIP] {asset_id} — already completed")
        return {"asset_id": asset_id, "status": "skipped"}

    # Token budget validation
    positive = item["positive"]
    negative = item["negative"]
    budget_ok, budget_detail = validate_token_budget(positive, negative)
    if not budget_ok:
        print(f"  [BUDGET] {asset_id}: {budget_detail}")
        # Trim to budget — truncate positive prompt words
        words = positive.split()
        while len(words) > MAX_POSITIVE_TOKENS:
            words.pop()
        positive = " ".join(words)
        neg_words = negative.split()
        while len(neg_words) > MAX_NEGATIVE_TOKENS:
            neg_words.pop()
        negative = " ".join(neg_words)
        _, budget_detail = validate_token_budget(positive, negative)
        print(f"  [TRIMMED] {asset_id}: {budget_detail}")

    # Dimensions
    dims = item.get("dimensions", DIM_SQUARE)
    width, height = dims

    # Base seed
    base_seed = seed_from_id(asset_id)

    # Retry loop
    for attempt in range(MAX_RETRIES):
        seed = base_seed + attempt
        try:
            print(f"  [{category}] {asset_id} (attempt {attempt+1}/{MAX_RETRIES}, seed={seed})")

            # Build workflow
            wf = build_workflow(
                workflow_template,
                positive_prompt=positive,
                negative_prompt=negative,
                seed=seed,
                width=width,
                height=height,
            )

            # Submit to ComfyUI
            prompt_id = client.queue_prompt(wf)
            print(f"    Queued: {prompt_id}")

            # Wait for completion
            result = client.poll_completion(prompt_id, max_wait=300.0)

            # Extract output filename from result
            outputs = result.get("outputs", {})
            image_filename = None
            for node_id, node_output in outputs.items():
                images = node_output.get("images", [])
                if images:
                    image_filename = images[0].get("filename")
                    image_subfolder = images[0].get("subfolder", "")
                    break

            if not image_filename:
                raise RuntimeError(f"No image output in result for {asset_id}")

            # Download image
            image_data = client.download_image(image_filename, subfolder=image_subfolder)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(image_data)
            print(f"    Saved: {out_path} ({len(image_data)} bytes)")

            # QC check
            qc_result = run_panel_qc(out_path, min_width=256, min_height=256)
            if qc_result["passed"]:
                progress.record(asset_id, category, "completed", str(item["path"]), seed)
                print(f"    QC: PASSED")
                return {
                    "asset_id": asset_id,
                    "status": "completed",
                    "path": str(item["path"]),
                    "seed": seed,
                    "qc": qc_result,
                }
            else:
                print(f"    QC: FAILED — {qc_result.get('checks', [])}")
                if attempt < MAX_RETRIES - 1:
                    print(f"    Retrying with seed+1...")
                    continue

        except Exception as e:
            print(f"    ERROR: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"    Retrying with seed+1...")
                time.sleep(2)
                continue

    # All retries exhausted
    failures.record(asset_id, category, MAX_RETRIES, "QC failed or generation error after all retries")
    progress.record(asset_id, category, "failed", str(item["path"]), base_seed)
    print(f"    FAILED after {MAX_RETRIES} attempts: {asset_id}")
    return {"asset_id": asset_id, "status": "failed"}


def generate_category(
    client: ComfyUIClient,
    category: str,
    output_dir: Path,
    *,
    progress: ProgressTracker,
    failures: FailureTracker,
    resume: bool = True,
) -> list[dict[str, Any]]:
    """Generate all images for a category."""
    if category not in CATEGORY_MAP:
        print(f"Unknown category: {category}")
        return []

    items = CATEGORY_MAP[category]()
    print(f"\n{'='*60}")
    print(f"CATEGORY: {category} ({len(items)} images)")
    print(f"{'='*60}")

    # All categories use txt2img (IP adapter not available on Pearl Star)
    workflow_template = load_workflow(WORKFLOW_TXT2IMG)

    results = []
    for item in items:
        result = generate_single(
            client, item, output_dir, workflow_template,
            progress=progress, failures=failures, resume=resume,
        )
        results.append(result)
        # Small delay between generations to avoid overloading GPU
        if result.get("status") == "completed":
            time.sleep(1.0)

    completed = sum(1 for r in results if r["status"] == "completed")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "failed")
    print(f"\n  {category} summary: {completed} completed, {skipped} skipped, {failed} failed")

    return results


# ═══════════════════════════════════════════════════════════════════
# Anchor panel metadata
# ═══════════════════════════════════════════════════════════════════

def write_anchor_metadata(output_dir: Path, results: list[dict[str, Any]]):
    """Write metadata JSON for each anchor panel."""
    anchor_items = get_anchors()
    for item in anchor_items:
        asset_id = item["asset_id"]
        matching = [r for r in results if r.get("asset_id") == asset_id and r.get("status") == "completed"]
        if not matching:
            continue
        r = matching[0]
        prompt_text = item["positive"]
        prompt_hash = f"sha256:{hashlib.sha256(prompt_text.encode()).hexdigest()}"
        metadata = {
            "panel_id": asset_id,
            "image_path": item["path"],
            "anchor_category": item.get("anchor_category", ""),
            "linework_weight_px": None,
            "shadow_coverage_pct": None,
            "contrast_ratio": None,
            "highlight_coverage_pct": None,
            "generation_seed": r.get("seed", 42),
            "prompt_hash": prompt_hash,
            "notes": "Run image metrics after generation",
        }
        meta_path = output_dir / f"anchor_panels/{asset_id}_metadata.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print(f"  Wrote anchor metadata: {meta_path}")


# ═══════════════════════════════════════════════════════════════════
# Asset registry builder
# ═══════════════════════════════════════════════════════════════════

def write_asset_registry(output_dir: Path, progress: ProgressTracker):
    """Write asset_registry.json from completed progress entries."""
    registry: dict[str, Any] = {
        "brand_id": BRAND_ID,
        "locale": LOCALE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ip_adapter_available": False,
        "ip_adapter_note": "Pearl Star ComfyUI has no IPAdapter nodes installed; all images generated with txt2img workflow",
        "character_refs": {},
        "location_refs": {},
        "prop_refs": {},
        "motif_refs": {},
        "atmospheric_refs": {},
        "panel_refs": {
            "covers": [],
            "chapter_openers": [],
            "silence": [],
        },
        "anchor_refs": [],
        "total_assets": 0,
        "categories_complete": [],
    }

    # Parse progress TSV
    completed_items: dict[str, list[dict[str, str]]] = {}
    if progress.path.is_file():
        for line in progress.path.read_text(encoding="utf-8").splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 4 and parts[2] in ("completed", "passed"):
                cat = parts[1]
                if cat not in completed_items:
                    completed_items[cat] = []
                completed_items[cat].append({"asset_id": parts[0], "path": parts[3]})

    total = 0

    # Character refs
    model_sheet_paths = [i["path"] for i in completed_items.get("model_sheets", [])]
    expression_paths = [i["path"] for i in completed_items.get("expressions", [])]
    pose_paths = [i["path"] for i in completed_items.get("poses", [])]
    anchor_paths = [i["path"] for i in completed_items.get("anchors", [])]

    registry["character_refs"]["ahjan"] = {
        "model_sheets": model_sheet_paths,
        "expressions": expression_paths,
        "poses": pose_paths,
        "anchor_panel": anchor_paths[0] if anchor_paths else "",
        "ip_adapter_source": model_sheet_paths[0] if model_sheet_paths else "",
        "ip_adapter_weight": 0.85,
        "ip_adapter_status": "unavailable — nodes not installed on Pearl Star",
    }
    total += len(model_sheet_paths) + len(expression_paths) + len(pose_paths)

    # Location refs
    for item in completed_items.get("locations", []):
        registry["location_refs"][item["asset_id"]] = {"path": item["path"]}
        total += 1

    # Atmospheric refs
    for item in completed_items.get("atmospheric", []):
        registry["atmospheric_refs"][item["asset_id"]] = {"path": item["path"]}
        total += 1

    # Prop refs
    for item in completed_items.get("props", []):
        registry["prop_refs"][item["asset_id"]] = {"path": item["path"]}
        total += 1

    # Motif refs
    motif_groups: dict[str, list[str]] = {}
    for item in completed_items.get("motifs", []):
        # Extract motif base name: motif_bell_stage_1 → motif_bell
        parts = item["asset_id"].rsplit("_stage_", 1)
        motif_base = parts[0] if len(parts) == 2 else item["asset_id"]
        if motif_base not in motif_groups:
            motif_groups[motif_base] = []
        motif_groups[motif_base].append(item["path"])
        total += 1
    for motif_id, stages in motif_groups.items():
        registry["motif_refs"][motif_id] = {"stages": sorted(stages)}

    # Panel refs
    for cat in ("covers", "chapter_openers", "silence"):
        for item in completed_items.get(cat, []):
            registry["panel_refs"][cat].append({"asset_id": item["asset_id"], "path": item["path"]})
            total += 1

    # Anchor refs
    for item in completed_items.get("anchors", []):
        registry["anchor_refs"].append({"anchor_panel_id": item["asset_id"], "path": item["path"]})
        total += 1

    registry["total_assets"] = total

    # Categories complete
    expected_counts = {
        "model_sheets": 12, "expressions": 8, "poses": 16,
        "locations": 18, "atmospheric": 8, "covers": 4,
        "chapter_openers": 6, "silence": 8, "props": 12,
        "motifs": 18, "anchors": 6,
    }
    for cat, expected in expected_counts.items():
        actual = len(completed_items.get(cat, []))
        if actual >= expected:
            registry["categories_complete"].append(cat)

    # Write
    reg_path = output_dir / "asset_registry.json"
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"\nAsset registry written: {reg_path}")
    print(f"Total assets: {total}")
    print(f"Categories complete: {registry['categories_complete']}")
    return registry


# ═══════════════════════════════════════════════════════════════════
# Character model sheets JSON
# ═══════════════════════════════════════════════════════════════════

def write_character_model_sheets_json(output_dir: Path, progress: ProgressTracker):
    """Write character_model_sheets.json."""
    completed_ms = []
    completed_expr = []
    if progress.path.is_file():
        for line in progress.path.read_text(encoding="utf-8").splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 4 and parts[2] in ("completed", "passed"):
                if parts[1] == "model_sheets":
                    completed_ms.append(parts[3])
                elif parts[1] == "expressions":
                    completed_expr.append(parts[3])

    doc = {
        "schema_version": "1.0.0",
        "artifact_type": "character_model_sheets",
        "brand_id": BRAND_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "characters": [
            {
                "character_id": CHARACTER_ID,
                "display_name": "Ahjan",
                "style_archetype": "cozy_iyashikei",
                "model_sheets": completed_ms,
                "expression_range": completed_expr,
                "ip_adapter_weight": 0.85,
                "ip_adapter_status": "unavailable — nodes not installed on Pearl Star",
            }
        ],
    }
    path = output_dir / "character_model_sheets.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"Character model sheets JSON written: {path}")


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Stillness Press manga image bank on Pearl Star ComfyUI"
    )
    parser.add_argument(
        "--category", action="append", dest="categories",
        help="Category to generate (repeat for multiple). Use 'all' for everything.",
    )
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--comfyui-url", type=str, default="http://192.168.1.112:8188",
        help="ComfyUI API URL",
    )
    parser.add_argument(
        "--progress", type=Path, default=None,
        help="Progress TSV path (default: <out>/GENERATION_PROGRESS.tsv)",
    )
    parser.add_argument(
        "--resume", action="store_true", default=True,
        help="Skip already-completed assets (default: True)",
    )
    parser.add_argument(
        "--no-resume", action="store_false", dest="resume",
        help="Regenerate all assets even if previously completed",
    )
    parser.add_argument(
        "--workers", type=int, default=1,
        help="Concurrent workers (default: 1 — Pearl Star RTX 3060 handles 1 at a time)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be generated without submitting",
    )
    args = parser.parse_args()

    # Resolve categories
    categories = args.categories or ["all"]
    if "all" in categories:
        categories = ALL_CATEGORIES
    if "registry" in categories:
        categories = [c for c in categories if c != "registry"]
        write_registry = True
    else:
        write_registry = False

    # Paths
    output_dir = args.out
    progress_path = args.progress or (output_dir / "GENERATION_PROGRESS.tsv")
    failures_path = output_dir / "GENERATION_FAILURES.tsv"

    # Initialize trackers
    progress = ProgressTracker(progress_path)
    failures = FailureTracker(failures_path)

    # Dry run mode
    if args.dry_run:
        print("\n=== DRY RUN MODE ===\n")
        total = 0
        for cat in categories:
            if cat not in CATEGORY_MAP:
                print(f"Unknown category: {cat}")
                continue
            items = CATEGORY_MAP[cat]()
            print(f"\n{cat} ({len(items)} images):")
            for item in items:
                skip = " [SKIP]" if progress.is_done(item["asset_id"]) else ""
                ok, detail = validate_token_budget(item["positive"], item["negative"])
                budget = "✓" if ok else "✗ OVER"
                print(f"  {item['asset_id']}: {item['dimensions'][0]}x{item['dimensions'][1]} tokens={budget}{skip}")
            total += len(items)
        print(f"\nTotal: {total} images across {len(categories)} categories")
        return 0

    # Check ComfyUI health
    print(f"Connecting to ComfyUI at {args.comfyui_url}...")
    client = ComfyUIClient(args.comfyui_url)
    try:
        stats = client.check_health()
        print(f"ComfyUI {stats['system']['comfyui_version']} — "
              f"PyTorch {stats['system']['pytorch_version']}")
    except Exception as e:
        print(f"STOP: ComfyUI unreachable at {args.comfyui_url}: {e}", file=sys.stderr)
        print("Pearl Star must be online with ComfyUI running.", file=sys.stderr)
        return 1

    # Generate
    print(f"\nOutput: {output_dir}")
    print(f"Progress: {progress_path}")
    print(f"Categories: {categories}")
    print(f"Resume: {args.resume}")
    print(f"NOTE: IP Adapter not available — all images use txt2img workflow")

    all_results = []
    start_time = time.time()
    total_fail_count = 0

    for cat in categories:
        results = generate_category(
            client, cat, output_dir,
            progress=progress, failures=failures, resume=args.resume,
        )
        all_results.extend(results)

        cat_fails = sum(1 for r in results if r.get("status") == "failed")
        total_fail_count += cat_fails

        # Systematic failure check: >15 failed → STOP
        if total_fail_count > 15:
            print(f"\nSTOP: More than 15 images failed QC ({total_fail_count}). "
                  f"Systematic issue — review prompt template before continuing.",
                  file=sys.stderr)
            break

        # Write anchor metadata after anchors category
        if cat == "anchors":
            write_anchor_metadata(output_dir, results)

    elapsed = time.time() - start_time

    # Write registry if requested or if all categories completed
    if write_registry or "all" in (args.categories or []):
        write_asset_registry(output_dir, progress)
        write_character_model_sheets_json(output_dir, progress)

    # Summary
    completed = sum(1 for r in all_results if r.get("status") == "completed")
    skipped = sum(1 for r in all_results if r.get("status") == "skipped")
    failed = sum(1 for r in all_results if r.get("status") == "failed")

    print(f"\n{'='*60}")
    print(f"GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Completed:  {completed}")
    print(f"Skipped:    {skipped} (resume)")
    print(f"Failed:     {failed}")
    print(f"Total time: {elapsed:.1f}s ({elapsed/60:.1f}m)")
    print(f"Output:     {output_dir}")
    print(f"Progress:   {progress_path}")
    if failed > 0:
        print(f"Failures:   {failures_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
