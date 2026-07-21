# External Home Cleanup Audit — 2026-07-09

This note records the repo-backed decisions used to retire Phoenix Omega material that had been living loose under `/Users/ahjan/`.

## Promoted into the repo

| External source | Decision | Canonical repo outcome |
| --- | --- | --- |
| `/Users/ahjan/the_question_book_template.txt` | Preserved as prompt lineage. | Imported verbatim as `old_chat_specs/question_book_template_2025-01-13.txt`. |
| `/Users/ahjan/phoenix_workspace_archive_2026_03_28/downloads_reviewed/preserved_candidates/pearl_news_genz_prompts.md` | Compare/promote only. | Missing Gen Z opening and anti-filler guidance promoted into `docs/PEARL_NEWS_WRITER_SPEC.md`; source file itself not copied. |

## Preserved-candidate archive decisions

| Archive file | Decision | Canonical replacement or rejection basis |
| --- | --- | --- |
| `EI_Enlightened_Intelligence_Framework.docx` | Reject as direct import. | The file is a compare-only EI disclosure draft. Active EI framing already lives on main in `brand-wizard-app/src/components/onboarding/SystemOverview.jsx`, `docs/phoenix_protocol/Phoenix_Protocol_Marketing_System.md`, and `config/governance/system_registry.yaml`. |
| `somatic_narration_guide.docx` | Reject as direct import. | The file is body-first exercise narration guidance, not a live runtime artifact. Equivalent somatic/audio guidance already exists in `talp/analyze_intake/extracted_docx/SOMATIC_WRITER_SPEC.md`, `config/pearl_practice/exercise_templates.yaml`, `config/pearl_practice/component_templates.yaml`, and `config/exercises/exercise_metadata_registry.yaml`. |
| `Phoenix_Omega_v3.1_Corrected.xlsx` | Superseded. | Canonical investor workbook is `PHOENIX_OMEGA_INVESTOR_DD.xlsx` at repo root; do not keep parallel workbook drafts outside the repo. |
| `Phoenix_Omega_v3_EI_Pivot.xlsx` | Superseded. | Canonical investor / market workbook remains `PHOENIX_OMEGA_INVESTOR_DD.xlsx`; this older pivot draft should not survive as a second source of truth. |
| `pearl-news-freebie-pages.zip` | Reject as direct import. | Repo-backed freebies now live under `SOURCE_OF_TRUTH/freebies/templates/`, `config/freebies/`, and `artifacts/freebies/`; do not reintroduce an external zip bundle. |
| `cjk6_manga_stories_all.json` | Superseded. | CJK6 translation work was already promoted through the repo translation lanes and their documented branch promotion records; keep the repo-backed translation configs/history, not this loose export. |
| `manga_test_volume.pdf` | Reject as generated preview. | Preview output is not canonical source. Keep only repo-backed manga configs, scripts, and approved assets. |
| `ahjan_manga_panels_71.zip` | Reject as generated output bundle. | Generated panel bundles do not become source of truth unless deliberately ingested through a repo lane. No such lane is active here. |
| `workflow_api_00000000-0000-0000-0000-000000001111.json` | Reject as unrelated export. | This is a FLUX/ComfyUI image workflow export, not Phoenix Omega canonical source material. |

## External folder deletion basis

- `/Users/ahjan/pearl_prime_storefront_router_prompts` is superseded by repo-backed storefront docs, trackers, mockups, workflows, and CI.
- `/Users/ahjan/wt_reclaim_archive_20260620` contains copies of files already present on main plus stale variants.
- `/Users/ahjan/waystream_pilot` is a derivative generated manuscript/audit bundle; the same source IDs and prose lineage already exist in repo artifacts.
- `/Users/ahjan/book_pages`, `/Users/ahjan/path`, and `/Users/ahjan/actions-runner` are loose OCR/output/runner leftovers, not canonical repo inputs.
- `/Users/ahjan/phoenix_hygiene_bundle_20260703` is a redundant stash backup of material that still exists in the live repo stash list.

## Decision

This note, together with `artifacts/audit/LEGACY_TEMPLATE_INGEST_AUDIT.md` and the promoted Pearl News writer-spec changes, is the explicit record required before deleting the retired `/Users/ahjan/` archive material referenced by `docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md`.
