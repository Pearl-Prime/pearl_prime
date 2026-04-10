# Pearl Prime — Ebook Pipeline (complete operator guide)

**Entry:** `scripts/run_pipeline.py`  
**Registry:** `config/pipeline_registry.yaml` → `pipelines.ebook`  
**Authority:** `specs/PHOENIX_V4_5_WRITER_SPEC.md`, arc-first rules in repo docs.

---

## Before you start

1. `python3 scripts/pipeline/create_job.py --pipeline ebook --topic … --persona … --arc <master_arc.yaml> --locale en-US --workspace <DIR>`
2. `python3 scripts/pipeline/acknowledge_guide.py --workspace <DIR>`
3. Run: `python3 scripts/run_pipeline.py --arc … --topic … --persona … --workspace <DIR>`

Use **`--no-job-check`** only in CI or when debugging with the owner’s approval.

---

## Stages (job.json)

The monolithic CLI advances all ebook stages together on success:

- **preflight** — tuple viability, arc presence, teacher matrix (if teacher mode)
- **book_spec** — catalog planner output
- **format_plan** — structural/runtime format selection (V4 freeze aware)
- **compile** — assembly compiler / registry resolution
- **prose_render** — optional `--render-book`
- **quality_gate** — chapter flow, book pass, bestseller craft, scene gate (per `--quality-profile`)
- **freebie_gen** — optional HTML/PDF/EPUB/MP3 freebies
- **epub_build** — optional `scripts/release/build_epub.py`
- **distribute** — packaging hooks (optional)

---

## Required CLI (arc-first)

- **`--arc`** — path to master arc YAML under `config/source_of_truth/master_arcs/`
- **`--topic`** / **`--persona`** — canonical ids (or `--input` YAML)
- **`--quality-profile`** — `production` | `draft` | `debug`

Optional: `--teacher`, `--render-book`, `--render-dir`, `--generate-freebies`, locale and atoms overrides.

---

## Config map

| Path | Role |
|------|------|
| `config/source_of_truth/master_arcs/*.yaml` | Arc — sole compile authority |
| `config/identity_aliases.yaml` | Persona/topic aliases |
| `config/topic_engine_bindings.yaml` | Engine eligibility |
| `pearl_prime/modular_format_freeze.py` | V4 output-format freeze |
| `config/quality/*` | Gate thresholds |

---

## Common mistakes

- Running generators **without** `--arc`.
- Using **`--structural-format` / `--runtime-format`** under V4 freeze (blocked).
- Skipping **tuple viability** / teacher validation when `--teacher` is set.
- Treating **draft** quality as releasable — use `production` for shipping builds.

---

## If validation fails

Read STDERR gate names (chapter flow, book pass, bestseller craft, scene anti-genericity). Fix atoms/registry coverage or arc alignment; re-run with the same `--workspace` so `job.json` tracks the run.
