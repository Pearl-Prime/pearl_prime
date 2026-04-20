# Pearl News Product Contract

**Authority:** Pearl_Dev  
**Date:** 2026-04-19  
**Status:** Active — enforced by regression museum gates

---

## Invariants (blocking)

### INV-1: One article = exactly one topic

- Every article has a single `topic` field.
- The article prose addresses that one topic as its central subject.
- The article is generated from feed items pre-filtered to that single topic (`--topic` flag).

**Enforcement:** `run_article_pipeline.py --topic <topic>` discards all feed items not matching the specified topic after SDG classification.

---

### INV-2: One article = exactly one teacher

- Every article has a single `teacher_id` field (top-level) and a `teacher_used.teacher_id` field.
- The article byline (`.pn-byline`) names that one teacher.
- The article prose centers on that one teacher's perspective/voice.
- Other teachers MAY be cited contextually but are never listed as co-authors.
- The `interfaith_dialogue_report` template (≤5% of articles) uses a USLF group voice — this is the only permitted multi-voice exception and does not set `teacher_id`.

**Enforcement:** `pearl_news/pipeline/teacher_resolver.py:resolve_teacher()` picks exactly one teacher per article deterministically. The byline block is injected by `run_article_pipeline.py` post-assembly.

---

### INV-3: Language = teacher's assigned language

- Each teacher has an `assigned_language` defined in `pearl_news/config/teacher_language_map.yaml`.
- The article `language` field equals the teacher's `assigned_language`.
- The LLM router receives the teacher's language (not a guessed or defaulted value).
  - English teachers → Claude (via `ANTHROPIC_API_KEY`)
  - CJK6 teachers → Qwen on Pearl Star (`QWEN_BASE_URL`)

**Enforcement:** `scripts/pearl_news/run_daily_news_cycle.py` looks up `TEACHER_LANGUAGE[teacher_id]` and passes it as `--language` to the pipeline. The pipeline tags every item with `item["language"] = language` before assembly and expansion.

---

### INV-4: No duplicate topics within a run

- For a given daily cycle (morning or evening), each topic appears at most once.
- Two teachers may NOT write on the same topic in the same cycle unless explicitly dispatched as a "same-topic, two-perspectives" feature (future, requires explicit `allow_topic_sharing=True` flag — not implemented).
- The topic assignment is deterministic: same date + cycle → same plan on every retry.

**Enforcement:** `scripts/pearl_news/run_daily_news_cycle.py:allocate_teacher_topics()` produces a unique `(teacher → topic)` mapping using a seeded greedy algorithm before the cycle starts. Each teacher's pipeline call receives `--topic <their_assigned_topic>`.

---

### INV-5: Layout shell present

Every article's `content` HTML includes:
- `<div class="pn-byline">` — teacher name, tradition, language, date
- The article body (assembled prose)
- `<aside class="pn-sidebar">` — teacher card, topic label, CTA

WordPress page chrome (header, nav, footer) is provided by the BlogSite theme and is not part of the article JSON.

**Enforcement:** `run_article_pipeline.py` injects `byline_html` before the content body after teacher resolution (Step 4a).

---

### INV-6: Sidebar present

Every article's `content` HTML includes an `<aside class="pn-sidebar">` block with:
- Teacher name and tradition (`.pn-sidebar-teacher`)
- Topic label (`.pn-sidebar-topic`)
- CTA (`.pn-sidebar-cta`)

Every article's JSON includes a `sidebar` object with: `teacher_name`, `teacher_tradition`, `teacher_language`, `topic`.

**Enforcement:** `run_article_pipeline.py` appends `sidebar_html` after the content body and adds the `sidebar` dict to `article_payload`.

---

## Dispatch model

```
One Pearl News cycle = N articles
  where N = len(active_teachers) × 1 topic/cycle
  
Example (morning cycle, 10 teachers):
  10 teachers × 1 topic each = 10 articles
  → guaranteed unique (teacher, topic) pairs per cycle
  → each article has 1 teacher, 1 topic, 1 language
  → topic plan: seeded by (date, "morning") → stable on retry

Two cycles per day (morning + evening) = 20 articles/day max.
Topics in morning and evening cycles are independently allocated,
so the same teacher may write on different topics morning vs evening.
```

---

## Regression museum

All six invariants above have corresponding blocking entries in `config/governance/regression_museum.yaml` (section `pearl_news_*`) and detectors in `phoenix_v4/quality/regression_museum/pearl_news_detectors.py`.

Any PR that reintroduces a violation blocks CI.

---

## File cross-references

| Component | File |
|-----------|------|
| Topic filter | `pearl_news/pipeline/run_article_pipeline.py` (`--topic` arg + Step 2a) |
| Byline + sidebar injection | `pearl_news/pipeline/run_article_pipeline.py` (article payload build) |
| Topic allocator | `scripts/pearl_news/run_daily_news_cycle.py:allocate_teacher_topics()` |
| Teacher resolver | `pearl_news/pipeline/teacher_resolver.py:resolve_teacher()` |
| Teacher language map | `pearl_news/config/teacher_language_map.yaml` |
| Teacher roster | `pearl_news/config/teacher_news_roster.yaml` |
| Regression museum | `config/governance/regression_museum.yaml` |
| Detectors | `phoenix_v4/quality/regression_museum/pearl_news_detectors.py` |
| Tests | `tests/test_pearl_news_one_article_per_teacher.py` |
|       | `tests/test_pearl_news_topic_allocation_uniqueness.py` |
|       | `tests/test_pearl_news_language_routing.py` |
