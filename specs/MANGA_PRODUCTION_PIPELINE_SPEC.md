# SpiritualTech Systems: Production Pipeline Specification

**Version:** 1.0
**Date:** March 2026
**Audience:** Production Engineers, DevOps, Data Engineers, QA Leads
**Classification:** Confidential

---

## Executive Summary

The Production Pipeline orchestrates the generation of 1,000 unique manga books across 30 brands, 11 locales, 10 genres, and 5 seed series. This spec defines how books are batched, scheduled, distributed across cloud GPU infrastructure, validated at scale, and tracked from concept to publication.

**Scale Challenge:** 1,000 books × (5 series + additional narrative variation) × (multiple genres per series) × (11 locales) = massive parallel orchestration problem requiring batching, resource allocation, dependency management, and quality gates at multiple levels.

**Solution:** Multi-stage pipeline with batch-driven architecture, cloud GPU scaling, per-stage quality gates, and comprehensive manifest tracking.

---

## 1. Production Scale & Distribution

### 1.1 The 1,000-Book Target

```yaml
scale_target: 1000
composition:
  series_count: 5
  brands_per_series: 6  # avg (some 6, some 8, some 5)
  total_brands: 30
  locales: 11
  genres: 10
  unique_permutations: "5 series × 30 brands × 11 locales × 10 genres = 16,500 potential"

actual_production_mix:
  # NOT uniform. Weighted by market demand, therapeutic need, anti-spam
  series_001_distribution: 250  # "The Boy Who Stopped Running" is popular
  series_002_distribution: 200  # "Grieflight Atlas"
  series_003_distribution: 200  # "Identity Crossing"
  series_004_distribution: 175  # "Relational Root"
  series_005_distribution: 175  # "The Outsider's Room"
  total: 1000

genre_distribution_weighted:
  slice_of_life: 0.35  # most therapeutic manga
  psychological: 0.25
  philosophical: 0.15
  drama: 0.15
  other: 0.10

locale_distribution_weighted:
  en: 0.25  # largest market (English speakers)
  ja: 0.20  # home market for manga cultural authenticity
  es: 0.15
  de: 0.10
  fr: 0.08
  pt: 0.07
  zh: 0.07
  ko: 0.05
  it: 0.04
  ru: 0.02
  ar: 0.02

production_timeline: "12 weeks"
books_per_week: "~83 books"
parallel_batches: "up to 10 simultaneous batches"
```

### 1.2 Production Mix Strategy (Anti-Spam)

Not all 16,500 permutations are produced. Instead, production is strategically sampled to:
- Maximize therapeutic coverage (prioritize high-need categories)
- Maintain brand distinctiveness (no duplicate brand-genre-locale triplets)
- Balance locale representation (all locales available; popular ones more frequently)
- Respect series affinity (some brands match certain series better)

```yaml
production_sampling_strategy:
  principle: "strategic_coverage_not_exhaustive_enumeration"

  priority_matrix:
    tier_1_high_demand:
      - combination: [series_001, brand_anxiety_group, en, slice_of_life]
        estimated_books: 30
        rationale: "Burnout + English-speaking + slice-of-life is highest demand"

      - combination: [series_002, brand_grief_group, ja, psychological]
        estimated_books: 20
        rationale: "Grief content resonates in home market with psychological depth"

    tier_2_strategic_coverage:
      - combination: [all_series, anxiety_brands, all_locales, psychological]
        estimated_books: 200
        rationale: "Cover anxiety category across locales; psychological approach"

      - combination: [all_series, identity_brands, culturally_relevant_locales, drama]
        estimated_books: 150
        rationale: "Identity content prioritized in diverse locales"

    tier_3_long_tail:
      - combination: [all_series, less_common_brands, less_common_locales, niche_genres]
        estimated_books: remaining_250

production_constraint_validation:
  rule_1: "Never produce same brand_genre_locale triplet twice"
  rule_2: "Each brand produces in at least 3 different locales"
  rule_3: "Each locale receives books from at least 20 different brands"
  rule_4: "Each series is represented in at least 6 different locales"
  rule_5: "Genre distribution across entire corpus matches weighted distribution"
```

---

## 2. Batch Structure & Scheduling

### 2.1 Batch Definition

A production batch is the unit of work submitted to the cloud GPU cluster.

```yaml
batch:
  batch_id: "batch_001"
  sequence_number: 1
  status: "pending"  # pending | running | completed | failed | partial_failure
  created_at: "2026-03-21T10:00:00Z"
  started_at: null
  completed_at: null

  batch_composition:
    target_size: 100  # books per batch
    actual_size: 100
    books: [
      {
        book_id: "book_001",
        series_id: "series_001",
        brand_id: "brand_001",
        genre: "slice_of_life",
        locale: "en",
        chapters: 14
      },
      # ... 99 more books
    ]

  batch_dependencies:
    requires_brand_dna_configs: ["brand_001", "brand_002", ..., "brand_030"]  # all
    requires_series_bibles: ["series_001", "series_002", ..., "series_005"]  # all
    requires_teaching_library: "version_1.0"

  batch_constraints:
    max_same_brand_per_batch: 2
    max_same_genre_per_batch: 25  # keep genre diversity
    max_same_locale_per_batch: 30
    min_brand_diversity: 20  # at least 20 different brands in batch
    no_duplicate_brand_genre_locale: true

  estimated_compute_cost:
    gpu_hours: 150  # 100 books × 14 chapters × ~0.1 GPU hours per chapter
    cost_usd: 225  # at $1.50/GPU hour on Vast.ai
    timeline_hours: 24  # assuming 6 GPUs running in parallel

  resource_allocation:
    gpu_count: 6
    gpu_type: "A100"  # or RTX 4090 / H100 depending on availability
    vram_per_gpu: "40GB"  # minimum
    workers: 3
    memory_gb: 64
```

### 2.2 Batch Scheduling: Weekly Plan

```yaml
production_schedule_weeks_1_12:
  week_001:
    batches: [batch_001, batch_002, batch_003]  # 3 batches × 100 = 300 books
    total_books_week: 300
    focus: "Series 001 (Boy Who Stopped Running) — highest demand"
    gpu_utilization: "3 batches parallel, each on separate GPU cluster"

  week_002:
    batches: [batch_004, batch_005, batch_006, batch_007]
    total_books_week: 300
    focus: "Series 001 continuation + Series 002 intro (Grieflight Atlas)"

  week_003:
    batches: [batch_008, batch_009, batch_010]
    total_books_week: 250
    focus: "Series 002 + Series 003 (Identity Crossing) intro"

  # ... continues for 12 weeks
  # Batch density increases weeks 4-8, normalizes weeks 9-12 for final refinement

  cumulative_schedule:
    week_04: 300  # cumulative: 1200
    week_05: 300  # cumulative: 1500
    week_06: 250  # cumulative: 1750
    week_07: 200  # cumulative: 1950
    week_08: 150  # cumulative: 2100
    week_09: 100  # cumulative: 2200
    week_10: 50   # refinement/regeneration
    week_11: 30   # final QA pass
    week_12: 20   # buffer for failed batch regen

  target_completion: "2026-06-09"
```

### 2.3 Batch Diversity Validation

Before a batch is approved for production, it is validated against diversity requirements:

```yaml
batch_diversity_validation:
  algorithm: "pre_submission_checker"

  check_1_brand_distribution:
    requirement: "at least 20 different brands in batch_100"
    validation: "count(unique_brands) >= 20"
    action_on_fail: "reject batch; recompose"

  check_2_genre_distribution:
    requirement: "no more than 25 books of same genre"
    validation: "max(count_per_genre) <= 25"
    action_on_fail: "reject batch; rebalance genres"

  check_3_locale_distribution:
    requirement: "no more than 30 books of same locale"
    validation: "max(count_per_locale) <= 30"
    action_on_fail: "reject batch; rebalance locales"

  check_4_brand_genre_locale_uniqueness:
    requirement: "no duplicate (brand, genre, locale) triplets"
    validation: "count(unique_triplets) == batch_size"
    action_on_fail: "reject batch; find and remove duplicates"

  check_5_series_distribution:
    requirement: "series representation proportional to target distribution"
    validation: "each series appears in at least 5 books in batch_100"
    action_on_fail: "reject batch; rebalance series"

  example_valid_batch_composition:
    batch_100:
      brands: 22 different brands ✓
      genres: {slice_of_life: 35, psychological: 25, philosophical: 15, drama: 15, other: 10} ✓
      locales: {en: 25, ja: 20, es: 15, de: 10, fr: 8, pt: 7, zh: 7, ko: 5, it: 4, ru: 2, ar: 2} ✓
      series: {s1: 30, s2: 25, s3: 25, s4: 12, s5: 8} ✓

  example_invalid_batch_composition:
    batch_50:
      brands: 8 different brands ✗ (need >= 20)
      reason: "batch rejected due to insufficient brand diversity"
```

---

## 3. Agent Orchestration & Dependency Graph

### 3.1 Pipeline Stages

```
STAGE 1: BATCH COMPOSITION & VALIDATION (Sequential, 2 hours)
├─ Compose batch_N with diversity constraints
├─ Validate batch diversity
├─ Generate batch manifest
└─ Approve for production

STAGE 2: PROMPT GENERATION (Parallel across batch, 4 hours)
├─ For each book in batch:
│  ├─ Load Series Bible for book.series_id
│  ├─ Load Brand DNA for book.brand_id
│  ├─ Load Genre constraints for book.genre
│  ├─ Load Teaching Library for wisdom atoms
│  ├─ Story Architect: Generate chapter-by-chapter narrative outline
│  ├─ Genre Agent: Apply genre conventions
│  ├─ Visual Identity Agent: Generate visual style specification
│  └─ Save prompt manifest for book
└─ Submit all chapter prompts to GPU queue

STAGE 3: IMAGE GENERATION (Parallel on cloud GPU, 16-24 hours)
├─ For each chapter in batch (1400 chapters total per 100-book batch):
│  ├─ Generate panel prompts from Story Architect output
│  ├─ Submit to Flux/SDXL on RunPod GPU cluster
│  ├─ Receive generated panel images
│  ├─ Store images in cloud storage (GCS/S3)
│  └─ Track generation success/failure
└─ Monitor GPU utilization; spawn additional workers if queue backlog

STAGE 4: LAYOUT & COMPOSITION (Parallel, 8 hours)
├─ For each chapter:
│  ├─ Layout Agent: Arrange panels on page per series formula
│  ├─ Apply lettering and SFX (from Brand DNA)
│  ├─ Compose final chapter images (manga pages)
│  └─ Store chapter pages
└─ Generate page manifest

STAGE 5: BATCH QC (Parallel per-book, 6 hours)
├─ For each book:
│  ├─ Per-chapter validation (page density, silence weight, motif presence)
│  ├─ Cross-chapter consistency (character visuals, arcs, atoms)
│  ├─ Brand DNA compliance (visual fingerprint, lettering, color)
│  ├─ Series Bible compliance (all 13 QC rules)
│  ├─ Anti-spam validation (visual similarity to existing corpus)
│  └─ Generate QC report
├─ Flag failures for regeneration
└─ Approve passing books for batch completion

STAGE 6: BATCH MANIFEST & METADATA (2 hours)
├─ Generate batch completion manifest
├─ Calculate batch statistics (diversity metrics, quality scores)
├─ Update production tracking database
└─ Archive batch artifacts

TIMELINE: One batch (100 books, 1400 chapters) = ~36-40 hours wall-clock time
         with 6 parallel GPU workers = ~36 hours
         3 batches in parallel on separate GPU clusters = 3 batches per 36 hours
```

### 3.2 Agent Dependencies

```yaml
agent_orchestration:
  batch_composer:
    stage: 1
    parallelism: "sequential (single instance)"
    consumes:
      - production_mix_constraints
      - brand_affinity_matrix
    produces:
      - batch_manifest (list of 100 books with metadata)

  story_architect:
    stage: 2
    parallelism: "embarrassingly parallel (1 instance per book)"
    instance_count: 100  # one per book in batch
    consumes:
      - series_bible (for book.series_id)
      - teaching_library (wisdom atoms)
      - genre_constraints
    produces:
      - chapter_outlines (14 chapters × narrative beats)
      - wisdom_atom_deployment (which atoms in which chapters)
      - narrative_prompts (text for image generation)

  genre_agent:
    stage: 2
    parallelism: "embarrassingly parallel (1 instance per book)"
    instance_count: 100
    consumes:
      - narrative_outline (from Story Architect)
      - genre_specification (e.g., slice_of_life conventions)
    produces:
      - genre_adapted_outline
      - genre_constraints (pacing, tone, narrative conventions)

  visual_identity_agent:
    stage: 2
    parallelism: "embarrassingly parallel (1 instance per book)"
    instance_count: 100
    consumes:
      - brand_dna (visual style, lettering, color)
      - series_bible (visual motifs, character designs)
      - genre_visual_conventions
    produces:
      - visual_style_specification (color palette, linework, shading rules)
      - panel_density_specification (panel count per page per section)
      - character_visual_registry (character appearance specs)
      - motif_placement_schedule

  panel_image_generator:
    stage: 3
    parallelism: "massively parallel (6 GPU workers)"
    workers: 6  # on RunPod/Vast.ai cloud GPU
    gpu_type: "A100 40GB"
    consumes:
      - narrative_prompts (from Story Architect)
      - visual_style_spec (from Visual Identity Agent)
      - character_specs (from Visual Identity Agent)
    produces:
      - panel_images (PNG, 1200×900px per panel)
      - generation_log (success/failure per panel)

  layout_agent:
    stage: 4
    parallelism: "embarrassingly parallel (1 instance per chapter)"
    instance_count: 1400  # 100 books × 14 chapters
    consumes:
      - panel_images (from Panel Image Generator)
      - panel_density_spec (from Visual Identity Agent)
      - lettering_spec (from Brand DNA)
    produces:
      - page_layouts (arranged panels per page)
      - lettering_placements
      - sfx_placements

  lettering_agent:
    stage: 4
    parallelism: "embarrassingly parallel (1 instance per chapter)"
    instance_count: 1400
    consumes:
      - page_layouts
      - dialogue_text (from Story Architect)
      - sfx_dictionary (from Brand DNA per locale)
      - lettering_style_spec (fonts, bubble shapes)
    produces:
      - lettered_pages (with dialogue bubbles, SFX, narration)

  qc_agent:
    stage: 5
    parallelism: "embarrassingly parallel (1 instance per book)"
    instance_count: 100
    consumes:
      - completed_book (all 14 chapters)
      - series_bible (for QC rule validation)
      - brand_dna (for anti-spam validation)
      - existing_corpus (for similarity scoring)
    produces:
      - qc_report (per-book)
      - similarity_scores (visual + textual)
      - compliance_flags (pass/fail per rule)

  production_orchestrator:
    stage: "continuous"
    parallelism: "single instance (central)"
    consumes:
      - batch_manifests
      - qc_reports
      - gpu_cluster_status
    produces:
      - scheduling_decisions
      - batch_status_updates
      - resource_allocation_recommendations
```

### 3.3 Parallelism Strategy

```yaml
parallelism:
  level_1_batch_level:
    description: "Multiple batches running in parallel on separate GPU clusters"
    concurrent_batches: 3  # 3 batches simultaneously
    total_gpu_clusters: 3  # each batch on own cluster (could share in future)

  level_2_book_level:
    description: "100 books in batch processed in parallel at Story Architect stage"
    parallelism_factor: 100
    infrastructure: "cloud CPU/orchestration cluster (not GPU-intensive)"

  level_3_chapter_level:
    description: "1400 chapters across 100 books submitted in parallel to GPU queue"
    parallelism_factor: 1400
    infrastructure: "GPU cluster (up to 6 workers per batch)"

  level_4_panel_level:
    description: "Panel image generation is queue-based; GPU workers pull from queue"
    parallelism_factor: "up to 6 concurrent GPU workers"
    infrastructure: "RunPod/Vast.ai elastic GPUs"

  resource_scaling:
    dynamic_scaling: true
    rule_1: "If GPU queue depth > 500 panels, spawn additional GPU worker"
    rule_2: "If batch CPU utilization < 30%, consolidate batches to single orchestrator"
    rule_3: "If batch QC pass rate < 85%, investigate failure modes before next batch"
```

---

## 4. Cloud GPU Infrastructure: RunPod & Vast.ai Integration

### 4.1 GPU Cluster Architecture

```yaml
gpu_infrastructure:
  providers:
    - name: "RunPod"
      pricing_usd_per_hour: 1.50  # A100
      availability: "high"
      api_integration: "REST + SDK"

    - name: "Vast.ai"
      pricing_usd_per_hour: 1.20  # RTX 4090
      availability: "medium"
      api_integration: "REST API"

  cluster_configuration:
    gpu_type_primary: "A100_40GB"  # 40GB VRAM for large batch inference
    gpu_type_fallback: "RTX_4090_24GB"

    worker_pool:
      min_workers: 2
      max_workers: 6
      target_workers_per_batch: 6

    orchestration:
      queue_system: "Ray" or "Slurm"  # centralized job queue
      job_scheduler: "custom_batch_scheduler"

  cost_model:
    gpu_hours_per_batch_100_books:
      image_generation: 150  # 100 books × 14 chapters × 0.1 hours
      queueing_overhead: 10
      total: 160

    cost_per_batch: 160 * 1.50 = $240 per batch

    cost_per_1000_books:
      batches_needed: 10
      total_cost: 10 * $240 = $2400
      cost_per_book: $2.40
```

### 4.2 Batch Submission Workflow

```
STEP 1: LOCAL PROMPT GENERATION
┌─────────────────────────────────────────┐
│ Cloud CPU cluster (on-demand, cheap)    │
│ - Story Architect → narrative prompts   │
│ - Visual Identity Agent → style specs   │
│ - Generate 1400 panel prompts           │
│ Result: prompts.jsonl (batch manifest)  │
└─────────────────────────────────────────┘

STEP 2: CLOUD GPU QUEUE SUBMISSION
┌─────────────────────────────────────────┐
│ Push prompts.jsonl to GPU queue         │
│ Spin up 6 GPU workers on RunPod/Vast    │
│ Each worker pulls jobs from queue       │
│ Workers run Flux/SDXL image generation  │
│ Result: 1400 panel images (png files)   │
└─────────────────────────────────────────┘

STEP 3: IMAGE STORAGE & TRACKING
┌─────────────────────────────────────────┐
│ Cloud storage (GCS/S3)                  │
│ Organize: /batch_001/book_001/ch_01/    │
│ Track: generation_log.csv (success/fail)│
│ Store: metadata.json (prompt + hash)    │
└─────────────────────────────────────────┘

STEP 4: LOCAL LAYOUT & COMPOSITION
┌─────────────────────────────────────────┐
│ Cloud CPU cluster (on-demand)           │
│ - Layout Agent: Arrange panels on pages │
│ - Lettering Agent: Add dialogue/SFX     │
│ - Compose final chapter images          │
│ Result: 1400 chapter pages (png files)  │
└─────────────────────────────────────────┘

STEP 5: LOCAL QC
┌─────────────────────────────────────────┐
│ Cloud CPU cluster                       │
│ - QC Agent: Validate per-book           │
│ - Similarity scoring vs. corpus         │
│ - Generate QC reports                   │
│ Result: qc_report.json per book         │
└─────────────────────────────────────────┘
```

### 4.3 Example RunPod API Call

```python
# Pseudocode: Submit batch to RunPod

import runpod

batch_manifest = load_batch_manifest("batch_001.json")
prompts = generate_panel_prompts(batch_manifest)  # 1400 prompts

# Create RunPod endpoint for this batch
endpoint = runpod.create_endpoint(
    name="manga_generation_batch_001",
    gpu_count=6,
    gpu_type="A100_40GB",
    container_image="spiritualtech/manga_generator:latest"
)

# Submit prompts to queue
job_ids = []
for prompt in prompts:
    job = endpoint.run_async(
        input={
            "prompt": prompt["text"],
            "image_style": prompt["visual_style"],
            "negative_prompt": "blurry, low quality, distorted",
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "model": "flux_dev"
        }
    )
    job_ids.append(job.id)

# Monitor queue
while len(job_ids) > 0:
    completed = [jid for jid in job_ids if endpoint.check_status(jid) == "completed"]
    for jid in completed:
        result = endpoint.get_result(jid)
        save_image(result["image"], f"outputs/{jid}.png")
        job_ids.remove(jid)
    time.sleep(30)  # Poll every 30 seconds

endpoint.delete()  # Cleanup
```

---

## 5. Quality Gates & Validation Pipeline

### 5.1 Multi-Level QC Strategy

```yaml
quality_gates:
  level_1_per_panel:
    gate: "Image generation quality check"
    run_by: "GPU worker (automated)"
    checks:
      - image_dimensions_correct: "1200x900"
      - no_nans_in_image: "all pixels valid"
      - aesthetic_score: "> 0.7 (using aesthetic classifier)"
    action_on_fail: "Regenerate panel (up to 3 retries)"
    estimated_fail_rate: "5%"
    sla: "4-hour regeneration window"

  level_2_per_chapter:
    gate: "Chapter composition quality"
    run_by: "Layout Agent + QC Agent"
    checks:
      - page_count_correct: "19 pages"
      - panel_arrangement_valid: "no overlaps, proper flow"
      - lettering_legible: "text readable, correct placement"
      - silence_weight_correct: "white space % matches formula"
      - no_visual_artifacts: "no bleeding, distortion"
    action_on_fail: "Regenerate chapter (rebuild from panels)"
    estimated_fail_rate: "10%"
    sla: "8-hour regeneration window"

  level_3_per_book:
    gate: "Series Bible & Brand DNA compliance"
    run_by: "QC Agent"
    checks:
      - all_13_qc_rules_satisfied: "see Series Bible spec"
      - character_consistency: "visual design matches registry"
      - motif_deployment: "motifs appear in correct chapters"
      - wisdom_atom_deployment: "atoms in correct sequence"
      - color_palette_correct: "matches brand + series rules"
    action_on_fail: "Regenerate book (rebuild chapters as needed)"
    estimated_fail_rate: "8%"
    sla: "12-hour regeneration window"

  level_4_cross_book:
    gate: "Anti-spam similarity validation"
    run_by: "QC Agent"
    checks:
      - visual_similarity_score: "< 0.10 vs. all published books"
      - textual_similarity_score: "< 0.15 (semantic embedding)"
      - brand_fingerprint_match: "< 0.08 style token overlap"
    action_on_fail: "Book flagged for manual review; may be blocked from publication"
    estimated_fail_rate: "2%"
    sla: "manual review within 24 hours"

  level_5_batch_level:
    gate: "Batch diversity validation"
    run_by: "Batch Composer (pre-submission) + Production Orchestrator (post-completion)"
    checks:
      - brand_diversity: "min 20 unique brands"
      - genre_balance: "distribution within tolerance"
      - locale_coverage: "all locales represented"
      - no_duplicate_triplets: "zero (brand, genre, locale) duplicates"
      - series_representation: "proportional to target mix"
    action_on_fail: "Reject batch; recompose and resubmit"
    estimated_fail_rate: "< 1%" (pre-validation prevents most failures)
    sla: "4-hour recomposition"
```

### 5.2 QC Report Structure

Every book produces a detailed QC report:

```json
{
  "qc_report_id": "qc_book_001_batch_001",
  "book_id": "book_001",
  "batch_id": "batch_001",
  "timestamp": "2026-03-25T14:30:00Z",
  "overall_status": "PASS",

  "compliance_checks": {
    "series_bible_compliance": {
      "rule_1_page_density": "PASS",
      "rule_2_silence_weight_progression": "PASS",
      "rule_3_visual_motif_deployment": "PASS",
      "rule_4_wisdom_atom_deployment": "PASS",
      "rule_5_character_consistency": "PASS",
      "rule_6_somatic_mirroring": "PASS",
      "rule_7_no_extraneous_plot": "PASS",
      "rule_8_resolution_integrity": "PASS",
      "rule_9_dialogue_authenticity": "PASS",
      "rule_10_pacing_integrity": "PASS",
      "rule_11_color_consistency": "PASS",
      "rule_12_line_quality": "PASS",
      "rule_13_panel_composition": "PASS"
    },

    "brand_dna_compliance": {
      "visual_fingerprint": {
        "score": 0.92,
        "status": "PASS",
        "note": "Excellent brand distinctiveness"
      },
      "lettering_consistency": "PASS",
      "color_palette_adherence": "PASS",
      "anti_spam_constraints": "PASS"
    },

    "anti_spam_validation": {
      "visual_similarity_to_corpus": {
        "max_similarity_score": 0.08,
        "threshold": 0.10,
        "status": "PASS",
        "most_similar_book": "book_523"
      },
      "textual_similarity_to_corpus": {
        "max_similarity_score": 0.12,
        "threshold": 0.15,
        "status": "PASS"
      },
      "brand_fingerprint_overlap": {
        "max_overlap": 0.05,
        "threshold": 0.08,
        "status": "PASS"
      }
    },

    "production_mix_validation": {
      "batch_triplet_uniqueness": "PASS",
      "brand_count_in_batch": 25,
      "genre_balance": "PASS",
      "locale_coverage": "PASS"
    }
  },

  "chapter_level_validation": {
    "chapter_001": {
      "page_density": "9 panels (within 7-10 range) ✓",
      "silence_weight": "18% white space (< 20%) ✓",
      "motifs_present": ["phone_on", "shoes_laced", "grey_heaviness"],
      "status": "PASS"
    },
    // ... chapters 2-14
    "chapter_014": {
      "page_density": "2 panels (within 1-2 range) ✓",
      "silence_weight": "92% white space (>= 90%) ✓",
      "motifs_present": ["shoes_on_differently", "light_natural", "ma_very_strong"],
      "status": "PASS"
    }
  },

  "image_quality_metrics": {
    "mean_aesthetic_score": 0.85,
    "image_generation_success_rate": 0.98,  // 2% regenerated
    "aesthetic_failures": 0
  },

  "regeneration_log": {
    "panels_regenerated": ["ch_03_panel_5", "ch_07_panel_2"],
    "chapters_regenerated": [],
    "reason": "Aesthetic score below threshold; regenerated and revalidated"
  },

  "notes": "Book passes all validation gates. Ready for publication.",
  "approval_by": "qc_agent_v1.0",
  "next_step": "publish_to_database"
}
```

---

## 6. Production Tracking & Manifest System

### 6.1 Master Production Manifest

A central manifest tracks all 1,000 books through production stages:

```yaml
master_manifest:
  created_at: "2026-03-21T00:00:00Z"
  target_books: 1000
  production_timeline_weeks: 12

  status_summary:
    completed: 850
    in_progress: 100
    failed_regenerating: 25
    pending: 25

  batch_tracking:
    batch_001:
      status: "completed"
      created_at: "2026-03-21T10:00:00Z"
      completed_at: "2026-03-22T14:00:00Z"
      books: 100
      pass_rate: 0.98  # 98% passed QC on first try
      books_requiring_regeneration: [book_023, book_045, book_067]

    batch_002:
      status: "in_progress"
      started_at: "2026-03-22T15:00:00Z"
      estimated_completion: "2026-03-23T19:00:00Z"
      gpu_queue_depth: 287  # 1400 total panels, 287 remaining
      current_gpu_workers: 6
      gpu_worker_status: {
        worker_1: "generating_panel_1087",
        worker_2: "generating_panel_1088",
        worker_3: "generating_panel_1089",
        worker_4: "idle",
        worker_5: "idle",
        worker_6: "idle"
      }

    batch_003:
      status: "pending"
      scheduled_start: "2026-03-24T08:00:00Z"
      books: 100
      composition_status: "approved"

  cost_tracking:
    total_spent_usd: 8400  # 8 batches × $240 + overhead
    cost_per_book: 9.88
    remaining_batches: 2
    estimated_total_cost: 10 * $240 = $2400 + overhead ~$3000

  quality_metrics:
    avg_qc_pass_rate: 0.93
    avg_aesthetic_score: 0.87
    anti_spam_validation_pass_rate: 0.98
    similarity_anomalies: 0

  publication_status:
    books_published: 750
    books_ready_for_publication: 100
    books_in_final_qc: 50
```

### 6.2 Book-Level Tracking

Each book has a detailed progress record:

```yaml
book_001_progress:
  book_id: "book_001"
  series_id: "series_001"
  brand_id: "brand_001"
  genre: "slice_of_life"
  locale: "en"

  status: "published"
  progress_percentage: 100

  timeline:
    created_at: "2026-03-21T10:00:00Z"
    batch_composition_completed: "2026-03-21T10:30:00Z"
    prompts_generated: "2026-03-21T11:00:00Z"
    image_generation_started: "2026-03-21T12:00:00Z"
    image_generation_completed: "2026-03-21T18:00:00Z"
    layout_and_lettering_completed: "2026-03-21T20:00:00Z"
    qc_completed: "2026-03-21T22:00:00Z"
    published_at: "2026-03-22T08:00:00Z"

  stages:
    batch_composition:
      status: "completed"
      timestamp: "2026-03-21T10:30:00Z"

    prompt_generation:
      status: "completed"
      chapters_generated: 14
      timestamp: "2026-03-21T11:00:00Z"

    image_generation:
      status: "completed"
      panels_total: 126  # 14 chapters, avg 9 panels per chapter
      panels_generated: 126
      panels_regenerated: 2
      gpu_hours_used: 1.2
      timestamp: "2026-03-21T18:00:00Z"

    layout_and_lettering:
      status: "completed"
      chapters_completed: 14
      timestamp: "2026-03-21T20:00:00Z"

    qc:
      status: "completed"
      qc_report: "qc_book_001_batch_001.json"
      pass_status: "PASS"
      timestamp: "2026-03-21T22:00:00Z"

    publication:
      status: "published"
      database: "manga_production_db"
      url: "https://www.spiritualtech.com/manga/book_001"
      timestamp: "2026-03-22T08:00:00Z"

  cost_allocation:
    gpu_cost: 1.80  # 1.2 hours × $1.50/hour
    cpu_cost: 0.50  # overhead
    storage_cost: 0.10  # image storage
    total_cost: 2.40
```

---

## 7. Failure Handling & Regeneration

### 7.1 Failure Modes & Recovery

```yaml
failure_scenarios:
  scenario_1_panel_aesthetic_failure:
    trigger: "Panel fails aesthetic quality check (score < 0.7)"
    frequency: "~5% of panels"
    recovery:
      action: "Regenerate panel using updated prompt"
      max_retries: 3
      if_all_retries_fail: "Manual review; may require chapter redesign"
      sla: "4 hours"

  scenario_2_chapter_composition_failure:
    trigger: "Chapter layout fails (panels don't fit, text overlap, etc.)"
    frequency: "~10% of chapters"
    recovery:
      action: "Regenerate chapter layout; if persistent, regenerate all panels in chapter"
      max_retries: 2
      sla: "8 hours"

  scenario_3_book_qc_failure:
    trigger: "Book fails one or more QC rules"
    frequency: "~8% of books"
    recovery:
      action: |
        If rule failure is fixable (e.g., motif missing in chapter 9):
          - Regenerate specific chapter
          - Re-run QC
        If rule failure indicates design issue:
          - Escalate to Story Architect
          - Redesign narrative/visual approach
          - Regenerate affected chapters
      max_retries: 3
      sla: "12 hours"

  scenario_4_similarity_anomaly:
    trigger: "Book similarity score > 0.10 vs. existing book"
    frequency: "< 2% of books"
    recovery:
      action: |
        Review similarity report. Options:
        1. If false positive (different books flagged as similar):
           - Update similarity algorithm
           - Revalidate batch
        2. If genuine concern (too much overlap):
           - Regenerate book with modified prompt
           - Revalidate
        3. If irreconcilable:
           - Block book from publication
           - Recompose batch (remove this book, add new book)
      sla: "24 hours manual review"

  scenario_5_gpu_worker_failure:
    trigger: "GPU worker crashes mid-batch"
    frequency: "< 1% per batch"
    recovery:
      action: |
        - Detect: Health check every 30 seconds
        - Terminate: Kill failed worker
        - Recover: Requeue jobs from failed worker
        - Spawn: Launch replacement GPU worker
        - Continue: Resume batch processing
      automatic_recovery: "yes"
      sla: "2 minutes (automated)"

  scenario_6_batch_diversity_failure:
    trigger: "Batch fails diversity validation (pre-submission)"
    frequency: "< 1% of batches (caught before submission)"
    recovery:
      action: |
        - Identify: Which constraint was violated?
        - Recompose: Swap books to restore diversity
        - Revalidate: Run diversity checker again
        - Resubmit: Submit revised batch
      sla: "4 hours"
```

### 7.2 Regeneration Priority Queue

When multiple books need regeneration, they are prioritized:

```yaml
regeneration_priority:
  priority_1_critical:
    condition: "Book failed multiple QC rules"
    action: "Regenerate immediately; may regenerate entire book"
    queue_position: "front_of_queue"

  priority_2_high:
    condition: "Book failed 1-2 individual chapters"
    action: "Regenerate failed chapters; re-run chapter + book QC"
    queue_position: "second_in_queue"

  priority_3_medium:
    condition: "Book has panels marked for regen (aesthetic score < 0.7)"
    action: "Regenerate panels; re-run chapter layout"
    queue_position: "normal_queue"

  priority_4_low:
    condition: "Book passed all QC but has cosmetic issues"
    action: "Optional enhancement; can skip if time is critical"
    queue_position: "deferred_queue"

  batch_wide_regeneration:
    condition: "Entire batch fails diversity validation"
    action: "Recompose batch; do not regenerate individual books"
    recovery_time: "4 hours (prompt generation stage only)"
```

---

## 8. Colab Prototype → Production Pipeline Transition

### 8.1 Colab Notebook Prototype

The development pipeline runs in Google Colab:

```python
# Colab Notebook: manga_generation_prototype.ipynb

import anthropic
import torch
from diffusers import FluxPipeline
import json

# SETUP
client = anthropic.Anthropic()
device = "cuda" if torch.cuda.is_available() else "cpu"
flux = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16)
flux.to(device)

# LOAD CONFIGS
series_bible = json.load(open("series_001_the_boy_who_stopped_running.json"))
brand_dna = json.load(open("brand_001_stillness_harbor.json"))
teaching_library = json.load(open("teaching_library.json"))

# SINGLE BOOK GENERATION (Prototype)
book_id = "prototype_001"
series_id = "series_001"
brand_id = "brand_001"

# Step 1: Story Architect (Claude API)
story_prompt = f"""
Generate narrative outline for chapter 1 of {series_bible['title']}.
Therapeutic wound: {series_bible['primary_wound']}
Wisdom atom: impermanence (anicca)
Characters: {series_bible['character_registry']}
Narrative beat: Protagonist under pressure, running
"""
story_response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    messages=[{"role": "user", "content": story_prompt}]
)
narrative_outline = story_response.content[0].text

# Step 2: Visual Identity Agent (rules + Claude)
visual_spec = {
    "color_palette": brand_dna["color_mode"],
    "linework": brand_dna["linework"]["stroke_weight"],
    "shading": brand_dna["shading"]["primary_method"],
    "panel_density": 9  # chapter 1 uses 9 panels
}

# Step 3: Panel Generation (Flux)
panel_prompt = f"""
Manga panel in {brand_dna['rendering_era']} style.
Color mode: {brand_dna['color_mode']}.
Scene: {narrative_outline}.
Visual style: {brand_dna['linework']}.
Emotional tone: anxious, driven, tense.
"""

with torch.no_grad():
    panel_image = flux(
        prompt=panel_prompt,
        height=900,
        width=1200,
        guidance_scale=7.5,
        num_inference_steps=30,
        max_sequence_length=512,
        generator=torch.Generator().manual_seed(42)
    ).images[0]

panel_image.save(f"outputs/{book_id}_ch01_panel_01.png")

# Step 4: Layout Agent (simple grid logic)
chapter_panels = [panel_image] * 9  # would normally generate all 9
page_layout = arrange_panels_grid(chapter_panels, columns=3, rows=3)

# Step 5: Lettering Agent (simple Pillow)
from PIL import Image, ImageDraw, ImageFont
lettered_page = add_dialogue_and_sfx(
    page_layout,
    dialogue="I can't stop...",
    sfx="BUZZ BUZZ",
    font_family=brand_dna['lettering_style']['fonts']['dialogue'],
    bubble_shape=brand_dna['lettering_style']['bubble_shapes']['dialogue']
)

# Step 6: Simple QC Check
qc_status = validate_chapter_simple(lettered_page, series_bible)
print(f"QC Status: {qc_status}")

# Save
lettered_page.save(f"outputs/{book_id}_ch01_final.png")
print(f"Chapter generated: outputs/{book_id}_ch01_final.png")
```

### 8.2 Prototype → Production Migration

```yaml
migration_strategy:
  prototype_environment:
    runtime: "Google Colab notebook"
    gpu: "T4 (16GB, free)"
    throughput: "1 chapter every ~10 minutes"
    suitable_for: "single-book testing, visual iteration, QA"

  production_environment:
    runtime: "Kubernetes cluster + RunPod/Vast.ai"
    gpu: "A100 40GB (6 parallel workers)"
    throughput: "100 books (1400 chapters) every 36 hours"
    suitable_for: "mass generation, cost-optimized, fault-tolerant"

  migration_steps:
    step_1_containerize:
      task: "Convert Colab notebook to Docker image"
      includes:
        - Python dependencies (anthropic, torch, diffusers, etc.)
        - Model weights (FLUX, custom fonts)
        - Brand DNA configs (30 JSON files)
        - Series Bible configs (5 JSON files)
        - Teaching Library (wisdom atoms)
      output: "spiritualtech/manga_generator:v1.0 (Docker image)"

    step_2_orchestration:
      task: "Implement batch orchestration (Ray or Slurm)"
      includes:
        - Batch scheduler (composition, validation, submission)
        - Job queue (prompt queue → GPU workers)
        - Resource manager (scale workers up/down)
        - Manifest tracking (production database)
      output: "batch_orchestrator.py + config.yaml"

    step_3_infrastructure:
      task: "Setup cloud GPU cluster"
      includes:
        - RunPod endpoint creation
        - Vast.ai GPU pool integration
        - Cloud storage (GCS/S3) for images
        - Production database (PostgreSQL) for tracking
        - Monitoring/logging (Datadog/Prometheus)
      output: "infrastructure_as_code (Terraform)"

    step_4_testing:
      task: "End-to-end testing with small batch"
      includes:
        - Batch 0: 10 books (proof of concept)
        - Validate: All pipeline stages work end-to-end
        - Measure: GPU cost, timing, quality
        - Iterate: Fix any integration issues
      success_criteria: |
        - 10 books generated successfully
        - All books pass QC on first try
        - Cost/book within budget ($3-5)
        - Timing meets SLA (36 hours per 100-book batch)

    step_5_production_launch:
      task: "Scale to full 1,000-book production"
      launch_date: "after successful batch 0 testing"
      weekly_throughput: "~100 books per batch"
      total_timeline: "12 weeks to complete"
```

### 8.3 Cost Comparison: Colab vs. Production

```yaml
colab_prototype_cost:
  per_book_generation_time: "~10 minutes per chapter = 140 minutes (2.3 hours)"
  per_book_gpu_cost: "Free (Colab free tier T4)"
  per_1000_books_human_cost: "$10,000 (manually running 1000 books)"
  suitable_for: "single books, testing, demos"

production_runpod_cost:
  gpu_cost_per_book: $2.40  # (1400 panels / batch × $1.50/hr) / 100 books
  orchestration_overhead: $0.60
  storage_cost_per_book: $0.10
  total_cost_per_book: $3.10
  per_1000_books_cost: $3,100
  human_cost_per_1000_books: $0 (fully automated)
  total_cost: $3,100 (vs. $10,000+ for manual Colab)
  payoff: "Break-even at ~100 books; significant savings at 1,000"
```

---

## 9. Monitoring, Logging & Observability

### 9.1 Production Dashboard

```yaml
production_dashboard_metrics:
  real_time_batch_status:
    current_batch: "batch_002"
    progress: "287 / 1400 panels generated (20%)"
    eta_completion: "14 hours remaining"
    gpu_workers_active: 6 / 6
    gpu_utilization: 94%

  cost_tracking:
    total_spent_this_week: "$1,200"
    cost_per_book_ytd: $2.98
    budget_remaining: "$200"
    on_track: "yes"

  quality_metrics:
    avg_qc_pass_rate_this_week: 95%
    aesthetic_score_avg: 0.87
    similarity_anomalies: 0
    regeneration_rate: 7%  # 7% of books required regeneration

  failure_tracking:
    gpu_worker_failures: 0
    batch_composition_failures: 0
    qc_failures: 6 (all recovered)
    escalated_for_manual_review: 0

  time_tracking:
    batch_throughput: "2.8 batches per week"
    weeks_to_completion: "3.5 remaining"
    on_schedule: "yes"
```

### 9.2 Logging Strategy

```yaml
logging:
  batch_level_logs:
    location: "GCS/batch_logs/batch_001.log"
    content:
      - batch_composition_start
      - prompt_generation_start/complete
      - gpu_queue_submission
      - image_generation_progress
      - layout_completion
      - batch_qc_results
      - batch_manifest_saved

  book_level_logs:
    location: "GCS/book_logs/{book_id}.log"
    content:
      - chapter_generation_timeline
      - qc_check_results
      - similarity_scores
      - regeneration_events
      - final_status

  gpu_worker_logs:
    location: "RunPod endpoint logs"
    content:
      - job_assignment
      - generation_progress
      - errors/warnings
      - completion_status
      - performance_metrics (time, memory)

  alerting:
    conditions:
      - if gpu_utilization < 50% for 30min: "Alert: Underutilized cluster"
      - if batch_qc_pass_rate < 80%: "Alert: Quality degradation"
      - if similarity_anomaly detected: "Alert: Potential duplicate detected"
      - if gpu_worker_fails: "Alert: Investigate failure mode"
```

---

## 10. Implementation Roadmap

### 10.1 Timeline: 16-Week End-to-End (4 weeks dev, 12 weeks production)

```yaml
phase_1_infrastructure_setup_weeks_1_4:
  week_1_2:
    tasks:
      - Finalize Brand DNA configs for all 30 brands
      - Finalize Series Bibles for all 5 series
      - Containerize Colab notebook → Docker image
    outputs:
      - brand_dna/*.json (30 files)
      - series_bible/*.json (5 files)
      - spiritualtech/manga_generator:v1.0 Docker image

  week_3:
    tasks:
      - Setup cloud GPU infrastructure (RunPod account, API keys)
      - Implement batch orchestrator
      - Setup production database schema
    outputs:
      - RunPod endpoint configured
      - batch_orchestrator.py
      - production_db schema

  week_4:
    tasks:
      - End-to-end testing with batch_0 (10 books)
      - Debug & iterate
      - Finalize cost model
    outputs:
      - Successful batch_0 completion
      - Cost validation ($3/book)
      - Go/no-go decision for production

phase_2_production_weeks_5_16:
  week_5_8:
    batches: [batch_001, batch_002, batch_003, batch_004]
    total_books: 400
    focus: "High-demand content (series_001 burnout, en/ja locales)"

  week_9_12:
    batches: [batch_005, batch_006, batch_007, batch_008, batch_009, batch_010]
    total_books: 600
    focus: "Secondary content (series 2-5, diverse locales)"

  week_13_16:
    batches: [batch_011, batch_012, batch_013, batch_014, batch_015, batch_016, batch_017]
    total_books: 1000  # cumulative
    focus: "Final refinement, regeneration, buffer batches"

  production_completion: "2026-06-09 (week 12)"
  expected_final_corpus: "1,000 unique manga books"
```

### 10.2 Success Criteria

```
Production success defined by:
✓ 1,000 books completed on schedule (12 weeks)
✓ 95%+ average QC pass rate
✓ <3% anti-spam similarity anomalies
✓ Cost per book <$3.50
✓ 100% batch diversity validation pass rate
✓ 0 critical production failures (GPU cluster stable)
✓ All books contain correct wisdom atoms, series motifs, brand DNA
✓ Reader engagement metrics show >80% find content helpful
```

---

## 11. Appendix: Batch Submission Example

### 11.1 Example Batch Manifest

```json
{
  "batch_id": "batch_001",
  "sequence_number": 1,
  "created_at": "2026-03-21T10:00:00Z",
  "books": [
    {
      "book_id": "book_001",
      "series_id": "series_001",
      "series_title": "The Boy Who Stopped Running",
      "brand_id": "brand_001",
      "brand_name": "Stillness Harbor",
      "genre": "slice_of_life",
      "locale": "en",
      "chapters": 14,
      "total_panels": 126
    },
    {
      "book_id": "book_002",
      "series_id": "series_001",
      "brand_id": "brand_002",
      "brand_name": "Breath Returning",
      "genre": "psychological",
      "locale": "ja",
      "chapters": 14,
      "total_panels": 126
    },
    // ... 98 more books (total 100)
  ],
  "batch_statistics": {
    "unique_brands": 22,
    "unique_genres": 8,
    "unique_locales": 10,
    "series_distribution": {
      "series_001": 30,
      "series_002": 25,
      "series_003": 25,
      "series_004": 12,
      "series_005": 8
    }
  },
  "validation_status": "APPROVED"
}
```

---

*SpiritualTech Systems · Production Pipeline Spec v1.0 · Confidential*
