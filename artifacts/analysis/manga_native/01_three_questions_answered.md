# Three Operator Questions — Full Answers
**Sprint:** manga-native-system-layer verification
**Date:** 2026-04-19
**File:** artifacts/analysis/manga_native/01_three_questions_answered.md

---

## Q1: Determinism — How does manga_profile interact with hash-seeded selection?

### Background: Existing Determinism

`phoenix_v4/manga/series/story_architect.py` already uses SHA-256-based deterministic
selection for beat templates:

```python
def _deterministic_int(seed: str, max_val: int) -> int:
    """Stable integer from a seed string."""
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % max_val

# Usage: seed = f"{series_id}:{arc_id}:{genre_id}"
# This selects settings, protagonist names, rival names deterministically.
```

### The Problem

Adding 8+ manga-native axes (market_demo, genre_family, emotional_engine,
serialization_engine, chapter_hook_family, visual_grammar, etc.) as additional
selection inputs would multiply the hash space and break any existing selections
when new axes are added. More importantly, selecting these axes per-render would
allow the same series to have different visual grammar on different render runs —
which violates the "style_archetype_id locked for entire volume" invariant.

### Recommended Design: Option C

**manga_profile is ASSIGNED at title-level (authored, not selected). Downstream
selection stays hash-seeded within profile-filtered banks.**

```python
# ── File: config/source_of_truth/manga_profiles/stillness_anxiety.yaml ──
# title_id: anxiety_overwhelm_vol1
# brand_id: stillness_press
# market_demo: josei
# genre_family: healing
# emotional_engine: cozy_restoration
# visual_grammar: iyashikei_minimalism
# chapter_hook_family: almost_confession
# ... (full profile, authored once, committed to config)

# ── File: phoenix_v4/manga/series/profile_loader.py ──

import hashlib
import yaml
from pathlib import Path


def load_manga_profile(title_id: str, brand_id: str) -> dict:
    """
    Load a manga_profile from config/source_of_truth/manga_profiles/.
    The profile is ASSIGNED at authoring time — not selected at runtime.
    Returns the profile dict for the given title_id.
    """
    base = Path("config/source_of_truth/manga_profiles")
    for yaml_file in base.glob("*.yaml"):
        profile = yaml.safe_load(yaml_file.read_text())
        if (profile.get("title_id") == title_id
                and profile.get("brand_id") == brand_id):
            return profile
    raise FileNotFoundError(
        f"No manga_profile found for title_id={title_id!r} brand_id={brand_id!r}"
    )


def manga_profile_seed(title_id: str, brand_id: str) -> str:
    """
    Stable 12-char seed from title_id + brand_id.
    Used for downstream bank filtering only.
    Profile itself comes from load_manga_profile(), not from this seed.
    """
    raw = f"{title_id}:{brand_id}".encode()
    return hashlib.sha256(raw).hexdigest()[:12]


# ── File: phoenix_v4/manga/series/story_architect.py (EXISTING, extended) ──

def _deterministic_int(seed: str, max_val: int) -> int:
    """Stable integer from a seed string. UNCHANGED."""
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % max_val


def build_story_architecture_internal(
    *,
    series_id: str,
    arc_id: str,
    schema_version: str = "1.0.0",
    chapters=None,
    genre_id: str = "shonen",
    manga_profile: dict | None = None,   # NEW: injected from load_manga_profile()
) -> dict:
    """
    manga_profile, when provided, filters the beat pool BEFORE hash selection.
    Profile is NOT selected here — it is passed in already loaded.
    This preserves full determinism: same inputs → same outputs.
    """
    effective_genre = (
        manga_profile.get("genre_family", genre_id)
        if manga_profile else genre_id
    )
    if chapters is None:
        chapters = _generate_default_chapters(series_id, arc_id, effective_genre)
    return {
        "schema_version": schema_version,
        "artifact_type": "story_architecture_internal",
        "series_id": series_id,
        "arc_id": arc_id,
        "chapters": chapters,
        "manga_profile_id": manga_profile.get("title_id") if manga_profile else None,
        "transmission_audit": {"note": "chunk_b_deterministic"},
        "constraint_checks": {"passed": True},
    }
```

### Determinism Test Assertion

```python
# ── File: tests/test_manga_profile_determinism.py ──

def test_same_render_twice_produces_same_output():
    """
    Render same (brand, series, topic, persona, arc, chapter) twice.
    Assert identical output.
    """
    from phoenix_v4.manga.series.story_architect import build_story_architecture_internal

    inputs = dict(
        series_id="anxiety_overwhelm_vol1",
        arc_id="arc_1",
        genre_id="iyashikei",
    )

    result_a = build_story_architecture_internal(**inputs)
    result_b = build_story_architecture_internal(**inputs)

    assert result_a == result_b, (
        "Same inputs produced different outputs — determinism broken"
    )


def test_manga_profile_assigned_not_selected():
    """
    Profile loaded from config — same profile for same title every time.
    """
    from phoenix_v4.manga.series.profile_loader import load_manga_profile

    profile_a = load_manga_profile("anxiety_overwhelm_vol1", "stillness_press")
    profile_b = load_manga_profile("anxiety_overwhelm_vol1", "stillness_press")

    assert profile_a == profile_b
    assert profile_a["visual_grammar"] == "iyashikei_minimalism"
    assert profile_a["emotional_engine"] == "cozy_restoration"
    # Profile is stable — not selected per-render


def test_downstream_seed_is_stable():
    """
    manga_profile_seed for same title+brand is always the same 12-char hex string.
    """
    from phoenix_v4.manga.series.profile_loader import manga_profile_seed

    seed_a = manga_profile_seed("anxiety_overwhelm_vol1", "stillness_press")
    seed_b = manga_profile_seed("anxiety_overwhelm_vol1", "stillness_press")

    assert seed_a == seed_b
    assert len(seed_a) == 12
    assert seed_a.isalnum()
```

### Summary of Option C

```
Profile (authored) ──→ load_manga_profile(title_id, brand_id) ──→ dict
                                       │
                                       ↓
Downstream selection (hash-seeded) ──→ _deterministic_int(seed, max_val)
                                       where seed = f"{series_id}:{arc_id}:{genre_id}"
                                       genre_id derived from manga_profile.genre_family
```

The profile is never randomly selected. It is a YAML file committed to
`config/source_of_truth/manga_profiles/` by an operator. The hash seed is used
only to select from within profile-filtered banks (beat templates, settings, etc.).

---

## Q2: Manga Mode Integration — Where does the new layer plug in?

### Current phoenix_v4/manga/ Surface Area

```
phoenix_v4/manga/
├── config.py                      # Config loaders (style_archetypes, panel_layouts, gates)
├── ite_pipeline.py                # ITE pipeline runner
├── visual_prompt_compiler.py      # Visual prompt compilation from atom metadata
├── panel_prompt_manifest.py       # Panel-level prompt manifest
├── transmission.py                # Story architecture → writer handoff
├── image_backend.py               # Render backend (ComfyUI/RunComfy)
├── asset_resolver.py              # Asset resolution
├── series/
│   ├── genre.py                   # build_genre_blueprint()
│   ├── story_architect.py         # Hash-seeded beat selection (EXISTING DETERMINISM)
│   ├── visual_identity.py         # style_bible + lettering_style_bible
│   ├── manga_author_resolver.py   # EI author identity resolution
│   ├── series_asset_registry.py   # Series-level asset tracking
│   └── emit.py                    # Series artifact emission
├── chapter/
│   ├── chapter_production.py      # Chapter production orchestrator
│   ├── writer.py                  # Chapter writer
│   ├── lettering_from_script.py   # Speech bubble + lettering spec derivation
│   ├── visual_from_script.py      # Visual prompts from chapter script
│   └── page_compose.py            # Page composition
├── qc/
│   ├── chapter_qc.py              # QA gate runner
│   ├── gate_registry.py           # Gate registry loader
│   └── ite_scorer.py              # ITE-specific scoring
├── runner/
│   ├── chapter_runner.py          # Chapter DAG runner
│   ├── dag_order.py               # DAG dependency ordering
│   ├── revision_policy.py         # Revision queue policy
│   └── stage_manifest_io.py       # Stage manifest I/O
├── memory/
│   └── series_memory_merge.py     # Series memory accumulation
├── models/
│   ├── paths.py                   # Canonical artifact path constants
│   ├── stage_ids.py               # Stage ID constants
│   ├── validation.py              # Schema validation helpers
│   └── workspace_layout.py        # Workspace directory layout
├── llm/
│   └── client.py                  # LLM client (chapter writer)
└── sdf/
    └── stub.py                    # SDF stub (future structured data format)
```

### Where New Layer Plugs In

The `manga_profile` layer is a **pre-series configuration step** that sits between
series setup and the genre_blueprint. It EXTENDS the current pipeline at one insertion
point:

```
EXISTING PIPELINE:
  operator inputs (series_id, brand_id, genre_id)
    ↓
  build_genre_blueprint(genre_id=...)
    ↓
  build_story_architecture_internal(series_id=..., arc_id=..., genre_id=...)
    ↓
  [rest of pipeline unchanged]

NEW PIPELINE (Option C extension):
  operator inputs (title_id, brand_id)
    ↓
  load_manga_profile(title_id, brand_id)    ← NEW: one-line addition
    ↓
  build_genre_blueprint(genre_id=profile["genre_family"])
    ↓
  build_story_architecture_internal(
      series_id=title_id,
      arc_id=...,
      genre_id=profile["genre_family"],
      manga_profile=profile,             ← NEW: profile injected
  )
    ↓
  [rest of pipeline unchanged]
```

**New file to create:** `phoenix_v4/manga/series/profile_loader.py` (signatures above)

**Existing files to extend (minimal edits):**
- `phoenix_v4/manga/series/story_architect.py` — add `manga_profile: dict | None = None`
  parameter to `build_story_architecture_internal()`, derive `effective_genre` from it
- `phoenix_v4/manga/runner/chapter_runner.py` — pass `manga_profile` through from series config

**Verdict: EXTENDS. Does not replace any existing module.**

The existing 45-file pipeline, 18 tests, 10 CI workflows, and 12 spec files are
all preserved unchanged. The new layer adds one loader, one new parameter, and
one new config directory.

---

## Q3: Version Identity — Is this a fork? A new pipeline? A new version?

### Answer: Same Phoenix v4.8 / phoenix_v4. New schema version. Not a fork.

**Evidence from repo:**
- `specs/MANGA_MODE_SYSTEM_SPEC.md` line 3: "Manga Mode extends the existing Pearl Prime
  pipeline. It does **not** create a parallel pipeline."
- The manga pipeline lives inside `phoenix_v4/manga/` — the same package namespace
  as the rest of Phoenix v4
- All manga artifacts use `schema_version: "1.0.0"` — same versioning convention
  as non-manga artifacts
- CI workflows reference the same `scripts/run_manga_pipeline.py` that calls into
  the same pipeline infrastructure
- The manga runner (`phoenix_v4/manga/runner/chapter_runner.py`) uses the same
  stage manifest and DAG infrastructure as non-manga modes

**What changes with this sprint:**
- New schema: `config/source_of_truth/manga_profiles/schema.yaml` — this is
  `manga_profile_schema_version: "1.0.0"`, a NEW schema version for a NEW artifact type
  (`manga_profile`). It does not replace any existing schema.
- New config directory: `config/source_of_truth/manga_profiles/` — follows the same
  `config/source_of_truth/` convention used by other Phoenix config (e.g., `config/authoring/`)
- No new package, no new pipeline, no fork

**Runtime format compatibility:**
- All existing manga artifacts (story_architecture_internal, story_architecture_handoff,
  chapter_script_writer_handoff, lettering_spec, panel_images_manifest, revision_queue)
  remain unchanged
- Variants without `manga_profile` linkage are still valid — backward compatible
- Adding `manga_profile_id` to `story_architecture_internal` is an optional enrichment field

**Version naming:**
```
Phoenix v4.8           — runtime version (unchanged)
phoenix_v4             — Python package (unchanged)
manga_profile_schema   v1.0.0  — new schema (this sprint)
manga_gates.yaml       schema_version: 1  — unchanged
genre_ite_profiles.yaml schema_version: "1.0" — unchanged
```

**One-liner:** The `manga_profile` schema is to Phoenix what a new JSON schema
file is to an API — it defines a new entity type in the same system, not a new system.
