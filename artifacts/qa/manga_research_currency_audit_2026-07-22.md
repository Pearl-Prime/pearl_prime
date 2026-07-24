# Manga Research-Currency Audit — 2026-07-22

**Agent:** Pearl_QA
**Lane:** manga_research_currency_verify_20260722
**origin/main SHA at audit time:** `1020acd8745a37b9d3ecb2a5f4c5cc28da4d1ae4`
**Method:** grep/import trace only — every verdict below is backed by the exact
command and output shown. No inference from file dates or docstrings alone.

## Discovery report

Distinct "genre prompting" / "drawing tradition" config files under `config/manga/`:

| File | Authored | Cites research artifact? |
|---|---|---|
| `genre_prompt_cookbook.yaml` | schema_version 1.0, dated 2026-07-09 | Yes — `authority: MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10`, `research_sha: 12799deabe294baf1d9da00305c2a3d43620d946` |
| `genre_prompt_cookbook_v2.yaml` | dated 2026-05-19 (predates the above by ~7 weeks) | No — cites `PR #802` (FLUX KDP-cover negation fix), not a manga-panel research artifact |
| `drawing_tradition_per_genre.yaml` | pre-dates v3 cookbook | Own axis system (A_line…H_token_mapping); consumed by `genre_tradition.py` |

## Central finding — the premise needs correcting

**`genre_prompt_cookbook_v2.yaml` is not a stale predecessor of `genre_prompt_cookbook.yaml`.**
They are not competing versions of the same artifact — they cover two entirely
different rendering domains:

- `genre_prompt_cookbook.yaml` (v3, 2026-07-09) = **manga panel** prompting authority,
  built from research SHA `12799deabe`.
- `genre_prompt_cookbook_v2.yaml` (2026-05-19) = **KDP self-help book-cover**
  prompting (11 non-fragment covers: anxiety, sleep_anxiety, grief, boundaries,
  self_worth, overthinking, imposter_syndrome, burnout, courage), FLUX-only,
  built from PR #802's negative-prompt CLIP fix. See its own header:

  ```
  # Genre Prompt Cookbook v2 — KDP Self-Help Cover Regeneration
  # ... regenerating the 11 non-fragment KDP self-help book covers
  # ... at 1600x2560 portrait.
  ```

This is already correctly documented in-repo: `scripts/manga/prompt_authority.py`
line 4-5 states "distinct from `genre_prompt_cookbook_v2.yaml` for KDP covers."
The artifacts/research doc itself (`MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10.md`
line 71) records the same distinction as a "stale internal note" it closes.

**Also corrected: `artifacts/research/MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10.md`
line 71 is itself now stale** — it says `genre_prompt_cookbook.yaml` "does not exist
on origin/main." It exists today (dated 2026-07-09, one day before that research
doc). Not fixed in this lane (doc-content edit, not a code/render path issue); flagged
as a handoff item below.

## Callsite trace: manga render/production entry points → genre-config file actually read

Command:
```
grep -rn "prompt_authority\|genre_tradition\|genre_prompt_cookbook" \
  scripts/manga/run_chapter_visual.py scripts/manga/run_chapter_production.py \
  scripts/manga/assemble_from_bank.py scripts/manga/queue_panel_renders.py \
  scripts/manga/run_manga_chapter.py
```
Direct imports were empty in all five — none of the five entry points import the
genre-config modules directly. Traced one level deeper:

```
scripts/manga/run_chapter_visual.py     → phoenix_v4.manga.chapter.visual_from_script.compile_panel_prompts_from_chapter_script
scripts/manga/run_chapter_production.py → phoenix_v4.manga.chapter.chapter_production.produce_chapter_assets
                                              → imports phoenix_v4.manga.chapter.visual_from_script
scripts/manga/run_manga_chapter.py      → phoenix_v4.manga.runner.chapter_runner
                                              → imports phoenix_v4.manga.chapter.visual_from_script.compile_panel_prompts_from_chapter_script
```

`phoenix_v4/manga/chapter/visual_from_script.py` line 49:
```python
from phoenix_v4.manga.genre_tradition import genre_tradition_tokens
```
and calls `genre_tradition_tokens(...)` at line 337 for every panel (`genre_tradition_engaged`
gates whether tokens fold in — but the import/call is unconditional per panel evaluation).

`phoenix_v4/manga/genre_tradition.py` line 61:
```python
DEFAULT_COOKBOOK_PATH = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook.yaml"
```
— reads **v3**, the current research-backed cookbook. `preferred_panel_model()`
(line 156) reads `entry.get("preferred_model")` from this same v3 file.

**Verdict: LIVE.** All three canonical chapter-DAG entry points
(`run_chapter_visual.py`, `run_chapter_production.py`, `run_manga_chapter.py`)
converge on `visual_from_script.py` → `genre_tradition.py`, which reads
`genre_prompt_cookbook.yaml` (v3) exclusively. `genre_prompt_cookbook_v2.yaml`
is never referenced by this path.

`scripts/manga/assemble_from_bank.py` and `scripts/manga/queue_panel_renders.py`
do not import any genre-prompt-cookbook module at all (they consume already-composed
prompts / bank contracts and dispatch renders — grep confirms zero hits for
`prompt_authority|genre_tradition|genre_prompt_cookbook` in either file). They are
downstream of the prompt-composition step, not prompt-cookbook readers themselves.
No `scripts/pearl_star/worker/*.py` file imports a genre-prompt-cookbook module
either (they are generic ComfyUI/Ollama dispatch workers; grep for `manga` found
5 files, none reference cookbook/genre_tradition — they receive already-built
prompt strings from the queue).

### Secondary/pilot lane

`scripts/manga/prompt_authority.py` ("Shared research-backed prompt authority for
live manga render lanes") imports `phoenix_v4.manga.genre_tradition` directly and
is itself imported by two pilot/enqueue scripts:
- `scripts/manga/run_mecha_layered_pilot_v3.py`
- `scripts/manga/enqueue_crossgenre_real_layers.py`

Both are Tier-1 operator-present pilot/enqueue lanes, not the canonical chapter DAG,
but both correctly read v3 via the same `genre_tradition.py` module. **Verdict: LIVE, v3.**

## Callsite trace: `cookbook_v2_compose_prompt.py`

Command:
```
grep -rn "cookbook_v2_compose_prompt" . --include="*.py" --include="*.yaml" --include="*.yml"
```
Result (worktree noise from sibling sessions excluded):
```
tests/test_cookbook_v2_loader.py:163:  from cookbook_v2_compose_prompt import compose_positive, load_cookbook
tests/test_cookbook_v2_loader.py:186:  from cookbook_v2_compose_prompt import (...)
scripts/manga/cookbook_v2_compose_prompt.py:25-26  (its own CLI docstring, self-reference)
scripts/publish/identity_compose_prompt.py:4       (docstring prose only: "Layered on top of
                                                      cookbook_v2_compose_prompt.py" — NOT a code import)
```
Confirmed by direct grep of `scripts/publish/identity_compose_prompt.py` for any
`import cookbook_v2` / `from cookbook_v2` / `cookbook_v2_compose_prompt\.` — zero
hits. `identity_compose_prompt.py` has its own independent `_load_cookbook()`
function (line 62) that reads the same YAML path directly; it does not import or
call anything from `cookbook_v2_compose_prompt.py`.

**Verdict: DEAD.** `scripts/manga/cookbook_v2_compose_prompt.py` (the module/script)
has zero reachable callsites from any production or pilot entry point — only its
own test (`tests/test_cookbook_v2_loader.py`) and its own CLI self-reference.
Header marker added (see Actions Taken).

## Callsite trace: `genre_prompt_cookbook_v2.yaml` (the data file, independent of the compose script)

Command:
```
grep -rn "genre_prompt_cookbook_v2" . --include="*.py" --include="*.yaml" --include="*.yml" --include="*.md"
```
Live consumer found:
```
scripts/publish/identity_compose_prompt.py:44
    DEFAULT_COOKBOOK_PATH = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook_v2.yaml"
```
`identity_compose_prompt.py` is imported by `scripts/publish/render_imagery_for_template.py`
(line 255, non-test), which is in turn imported by:
```
scripts/publish/render_kdp_cover.py          (production KDP cover renderer)
scripts/publish/recover_devotion_epub_covers.py
scripts/publish/waystream_covers/pools.py
scripts/publish/brand_covers/pools.py
artifacts/waystream/cover_pilot/gen_pools.py
```
`test_publish_render_kdp_cover.py:299` also reads this YAML's raw text directly
(secondary, test-only reference; not the load-bearing one).

**Verdict: LIVE — but for KDP covers, not manga panels.** This file has a genuine,
current, non-test production consumer (`render_kdp_cover.py`'s cover-imagery
pipeline via `identity_compose_prompt.py`). It is correctly scoped to its stated
domain (KDP self-help covers) and is not competing with, superseding, or being
superseded by `genre_prompt_cookbook.yaml` (manga panels). **No `status: unwired`
or `superseded_by` marker was added to this YAML** — doing so would be false; the
file has an active, correctly-scoped consumer and `check_manga_wiring.py`'s own
non-test-consumer check already passes it honestly.

## Base-model (H_token_mapping) currency trace vs V5.1 architecture

`docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md` (status: AUTHORITY v1.0.0) names
Qwen-Image-Layered (`qwen_image_layered_fp8mixed.safetensors`) as the current
V5.1 primary render model, superseding the V4 L0+L2 split. `genre_tradition.py`
`_H_ENGINE_KEYS = ("flux_schnell", "qwen_image", "animagine_xl_4_0", "animagine")`
and `preferred_panel_model()` defaults to `qwen_image` — consistent with V5.1.

Checked every genre in `drawing_tradition_per_genre.yaml` (26 total) for whether
its `H_token_mapping` actually carries a `qwen_image` entry, cross-referenced
against each genre's `preferred_model` in `genre_prompt_cookbook.yaml` (v3):

```python
# all 26 genres' H_token_mapping keys:
healing, dark_fantasy, psychological_horror, mecha, romance, slice_of_life,
fantasy_adventure, comedy  → ['animagine_xl_4_0','qwen_image','flux_schnell',...]  (qwen present)

battle, sports, horror, essay, food, family, cultivation, sci_fi_cyberpunk,
school, memoir, battle_internal  → single-key stub ('animagine_starter' or
'flux_schnell_starter' only) — NO qwen_image key present

mystery, workplace, procedural, historical, supernatural_everyday,
social_issue, graphic_medicine → ['qwen_starter']  (qwen present, short form)
```

`genre_prompt_cookbook.yaml` (v3) explicitly declares `preferred_model: qwen_image`
for **all 11** of the no-qwen-key genres (`battle`, `sports`, `horror`, `essay`,
`food`, `family`, `cultivation`, `sci_fi_cyberpunk`, `school`, `memoir`,
`battle_internal`) — confirmed by direct read of each entry's `preferred_model`
field.

**This is a genuine live-path drift, not a doc/date artifact.** At render time,
`genre_tradition_tokens(genre_id, base_model="qwen_image")` is called (v3 cookbook
says qwen_image is correct for these genres). `_h_token_positive_negative()`
(genre_tradition.py line 181) looks for `H_token_mapping["qwen_image"]`, doesn't
find it, tries the `animagine_xl_4_0`→`animagine` alias (no match either), then
falls through to the bare `"<engine>_starter"` substring match — `base_model.split("_")[0]` is `"qwen"`, and the only key present is `"animagine_starter"` or
`"flux_schnell_starter"` (neither contains `"qwen"`), so **no match** — and the
function falls all the way through to `_synth_positive_from_blocks()`, a generic
line-weight/palette/mangaka-exemplar synthesis. The operator-curated,
engine-specific `H_token_mapping` string these 11 genres' cookbook entries expect
never fires; panels render on the generic fallback instead.

**Verdict: UNCLEAR-see-evidence, scoped fix identified.** Not a "wrong model
pinned" (no genre points at a model V5.1 has deprecated — `animagine_xl_4_0` and
`flux_schnell` both remain valid secondary engines per `_H_ENGINE_KEYS`) but a
**content gap**: 11 of 26 genres' `drawing_tradition_per_genre.yaml` blocks lack
the `qwen_image` `H_token_mapping` entry that their own `genre_prompt_cookbook.yaml`
`preferred_model: qwen_image` declaration requires, silently degrading those
genres to generic-synthesis tokens instead of curated ones on every live render.

**Not fixed in this lane** — this is render-behavior content (11 new curated
prompt strings), not a one-line import-path change, so per the landing contract
it is handed off rather than authored here. See handoff doc.

## Verdict summary

| Artifact | Verdict | Evidence |
|---|---|---|
| `genre_prompt_cookbook.yaml` (v3, manga panels) | **LIVE** everywhere in the canonical chapter DAG + pilot lane | `visual_from_script.py`→`genre_tradition.py`→`DEFAULT_COOKBOOK_PATH`; `prompt_authority.py` |
| `genre_prompt_cookbook_v2.yaml` (KDP covers) | **LIVE**, correctly scoped to a different domain — NOT stale, NOT superseded | `identity_compose_prompt.py`→`render_imagery_for_template.py`→`render_kdp_cover.py` |
| `scripts/manga/cookbook_v2_compose_prompt.py` | **DEAD** — zero reachable callsites outside its own test | grep trace above; header marker added |
| `drawing_tradition_per_genre.yaml` H_token_mapping | **LIVE**, current for 15/26 genres; **content gap** for 11/26 genres whose v3 `preferred_model: qwen_image` has no matching `qwen_image` H_token_mapping entry | Python cross-check above |

## Actions taken in this lane

1. Added a header status marker to `scripts/manga/cookbook_v2_compose_prompt.py`
   (mechanical, per the unwired-config-as-working CI gate's own convention) —
   confirmed dead, not deleted, per DO NOT instructions. Operator sign-off required
   before any deletion.
2. **Did not** add `status: unwired` / `superseded_by` to `genre_prompt_cookbook_v2.yaml`
   — the trace shows it has a genuine live, correctly-scoped consumer; marking it
   unwired would be false and would itself be a drift.

## Follow-on items (not actioned in this lane — handed off)

1. **Content gap (render-behavior fix, needs operator/craft review):** author
   `qwen_image` `H_token_mapping` entries in `config/manga/drawing_tradition_per_genre.yaml`
   for the 11 genres listed above (`battle`, `sports`, `horror`, `essay`, `food`,
   `family`, `cultivation`, `sci_fi_cyberpunk`, `school`, `memoir`, `battle_internal`),
   matching the curated-string quality of the 8 genres that already have all three
   engine keys. This is prompt-craft authoring, not a mechanical fix.
2. **Stale doc line:** `artifacts/research/MANGA_GENRE_PROMPTING_SYSTEM_RESEARCH_2026-07-10.md`
   line 71 asserts `genre_prompt_cookbook.yaml` "does not exist on origin/main" —
   it exists today. Low priority (historical research doc, not an authority doc
   consumed at render time) but worth a one-line correction note for future readers.
