# Cover packaging platform audit — Phoenix Omega

**Date checked (sources):** 2026-04-10  
**Project:** `proj_state_convergence_20260328`  
**Subsystem focus:** ebook pipeline, audiobook pipeline, release, repo coordination

## Executive summary

| Question | Finding |
|----------|---------|
| Are ebook covers embedded in EPUB? | **Yes** — `scripts/release/build_epub.py` uses `ebooklib` `set_cover` and ships `EPUB/cover.png` + `cover.xhtml` (verified on `artifacts/epub/ahjan_anxiety.epub`). |
| Are storefront covers produced separately? | **Partially** — Batch EPUB build reads `artifacts/pipeline_examples/<teacher>/cover_*.png` (not the only storefront path). `generate_showcase_bundle.py` emits **1600×2560** `cover_*_ebook.png` for showcase/manifest. `generate_bestseller_covers.py` defines KDP portrait + 3200 square audiobook. No single release CSV in repo enumerates all upload slots; manifest now labels roles explicitly. |
| Are audiobook covers square and separate from ebook? | **Yes (script intent)** — Showcase flow writes **3200×3200** `cover_*_audiobook.png` vs **1600×2560** `cover_*_ebook.png`. |
| Fixes applied this audit | EPUB embed **normalizes to 1600×2560** when Pillow is available (fixes prior 1024×1024 embed from square sources). DC description typo “audiobook” → “book”. Manifest adds `cover_ebook_storefront_rel` + `cover_role_notes`. |

**Phoenix Omega standard (recommended):**

1. **Ebook:** Portrait embed inside EPUB (1600×2560 after normalization) **plus** a separate storefront/master file for each distributor upload (JPEG for KDP upload where required).
2. **Audiobook:** Square master (≥2400×2400 for many distributors); export **JPG** where required (e.g. ACX). Do not reuse ebook portrait as the audiobook square without redesign.

---

## Platform matrix (official sources)

Legend: **Emb.** = interior/embedded EPUB cover; **Store** = file upload / marketing image separate from or in addition to book package.

| Platform | Ebook embedded cover | Separate ebook storefront cover | Audiobook cover rule | Repo compliant? | Notes |
|----------|---------------------|----------------------------------|----------------------|-----------------|-------|
| **Amazon KDP** | Expected as part of reflowable EPUB interior practice; KDP also takes manuscript + **separate** cover upload. | **Required** for detail page: JPEG/TIFF; ideal **2560 h × 1600 w**, min **1000 h × 625 w**, ratio **≥1.6:1**, &lt;50 MB, RGB 72 dpi (300 PPI recommended). | *eBook row:* N/A | **Yes** after embed normalization; operators must upload **JPEG/TIFF** per KDP (our default embed is PNG). | [What criteria does my eBook's cover image need to meet?](https://kdp.amazon.com/en_US/help/topic/G200645690) |
| **KDP Select** | Same title uses same KDP **content** setup; Select is exclusivity/royalty program. | Same as KDP **cover upload** (no separate Select-only cover spec found). | N/A | **Yes** (same as KDP) | Select does not change cover image criteria; see [KDP Select](https://kdp.amazon.com/en_US/select) for program scope vs [cover criteria](https://kdp.amazon.com/en_US/help/topic/G200645690). |
| **Google Play Books (ebook)** | **EPUB must contain the front cover image.** | **Yes** — even if cover is in EPUB, you may submit a separate file for thumbnails; cover min **640 px** dimension, max 7200 px; jpeg/png/tiff/pdf for cover files. | N/A | **Yes** for embed + storefront portrait path (`cover_*_ebook.png`); validate with EpubCheck per Google. | [Book file guidelines](https://support.google.com/books/partner/answer/3424254); [EPUB files](https://support.google.com/books/partner/answer/3316879) |
| **Google Play (audiobook / auto-narrated)** | N/A | N/A | **1:1** aspect; **2400×2400** recommended; jpeg/png; min 1024, max 7200. | **Yes** — we generate 3200 square PNG; operator can downscale to 2400 if matching “ideal” exactly. | [Upload or update a cover image](https://support.google.com/books/partner/answer/14187606); audiobook section in [Book file guidelines](https://support.google.com/books/partner/answer/3424254) |
| **Apple Books** | Interior cover subject to **5.6M pixel** interior image cap (same as other interior images). | **Marketing / external** cover is **not** the same as interior cover: delivered **with** asset; min **1400 px** on shorter side; RGB; JPEG or PNG; do not upscale small sources. | Audiobook art follows partner workflows; square marketing norms align with industry practice — confirm in Apple Books Partner at upload time. | **Yes** for separate high-res art paths; EPUB embed normalized to portrait reduces interior pixel count vs oversized bitmaps. | [Book Cover Art](https://help.apple.com/itc/booksassetguide/en.lproj/itc1bda991ba.html); [Formatting guidelines](https://help.apple.com/itc/applebooksstoreformatting/en.lproj/static.html) |
| **Kobo Writing Life** | EPUB typically includes cover; Kobo emphasizes **portrait** presentation. | Upload: **3:4** width:height (“width … is ¾ of its height”), JPG preferred / PNG ok, ≤5 MB, 300 DPI best. | N/A | **Partial** — KDP-ideal **1600×2560** is **5:8** (w/h=0.625), not Kobo **3:4** (w/h=0.75; e.g. **1920×2560**). Use a Kobo-specific export when targeting Kobo-first. | [Cover Image Tips](https://kobowritinglife.zendesk.com/hc/en-us/articles/360059385711-Cover-Image-Tips) |
| **B&N / NOOK Press (NOOK Book)** | EPUB/Nook submission as per publisher workflow. | FAQ: cover **≥750×750** min; **≥1400×1400** recommended; JPG/PNG; 5 KB–2 MB. | N/A | **Yes** for our masters (1600×2560 and 3200 square exceed mins). | [Where can I upload my cover image](http://www.nook.com/services/cms/doc/nookpress/us/en_us/faq/where-can-i-upload-my-cover-image.html) |
| **ACX / Audible** | N/A | N/A | **Square** cover art per Audible/ACX spec; official PDF lists technical requirements (typically **2400×2400** RGB **JPG**). | **Partial** — we output **3200 PNG**; operators should export **2400×2400 JPG** for ACX upload. | [Official Audible Cover Art Requirements (PDF)](https://images-na.ssl-images-amazon.com/images/G/01/Audible/en_US/acx/pdf/OfficialAudibleCover-ArtRequirements.pdf) |
| **Voices by INaudio / Findaway-style** | N/A | N/A | **Square**, **min 2400×2400**, PNG/TIF/JPG; **no borders/letterboxing**; title + author clearly visible. | **Partial** — resolution OK; **badge** “AUDIOBOOK” on showcase covers may conflict with “no format callouts” / design policies — use **unbadged** variant for distributor submission. | [Cover art technical requirements](https://voicessupport.inaudio.com/en/articles/3219584) |

### Kobo ratio correction (repo gap)

Kobo states width should be **¾ of height** (3:4 aspect). KDP’s stated ideal **1600×2560** has width/height = **0.625** (5:8), not 0.75. Operators who care about Kobo-first layout should generate an additional **1920×2560** (or scale) storefront asset; this is **not** auto-generated in the repo today.

---

## Repo behavior (evidence)

### `scripts/release/build_epub.py`

- Embeds cover via `book.set_cover("cover.png", …, create_page=True)`.
- **Change (2026-04-10):** `prepare_embedded_ebook_cover()` letterboxes sources to **1600×2560** when Pillow is installed (`--raw-cover` to disable).
- **Validation:** Rebuilt sample EPUB from `artifacts/pipeline_examples/ahjan/cover_ahjan_anxiety.png` (1024×1024); embedded `EPUB/cover.png` measured **1600×2560** (PIL after rebuild to `/tmp/test_norm.epub`).
- Prior committed `artifacts/epub/ahjan_anxiety.epub` contained **1024×1024** embed — **re-run** `--batch` or per-book CLI to refresh committed EPUBs when ready.

### `scripts/audiobook/generate_showcase_bundle.py`

- `run_covers`: writes `cover_{tid}_{topic}_audiobook.png` (3200×3200) and `cover_{tid}_{topic}_ebook.png` (1600×2560) under `brand-wizard-app/public/assets/covers/audiobook/`.
- **Change:** `manifest.json` teacher rows include `cover_ebook_storefront_rel` and `cover_role_notes`.

### `scripts/image_generation/generate_bestseller_covers.py`

- Defines `kdp_ebook` **1600×2560** and `audiobook_square` **3200×3200** — aligned with KDP ideal and high-res square audiobook workflow.

### `scripts/video/render_audiobook.py`

- No cover asset; video-only. No change required.

### `artifacts/epub/pattern_library/`

- Path **not present** in this checkout (empty or omitted). No additional pattern-library manifests to audit.

---

## Validation commands (reference)

```bash
# EPUB zip layout
unzip -l artifacts/epub/ahjan_anxiety.epub | head -25

# Cover dimensions inside EPUB
python3 -c "import zipfile,io; from PIL import Image; z=zipfile.ZipFile('artifacts/epub/ahjan_anxiety.epub'); print(Image.open(io.BytesIO(z.read('EPUB/cover.png'))).size)"

# Refresh EPUB after normalization fix
python3 scripts/release/build_epub.py --batch
```

---

## Remaining gaps

1. **Committed EPUBs** in `artifacts/epub/` may still hold pre-fix cover dimensions until batch-regenerated.
2. **KDP cover upload** JPEG/TIFF vs **EPUB** PNG embed — operators keep both roles in mind.
3. **Kobo 3:4** vs **KDP 5:8** ideal — optional second storefront master (e.g. 1920×2560) not generated automatically.
4. **ACX** prefers **JPG** at **2400×2400** — add export step or future `--acx-cover` flag if desired.
5. **Distributor badge** on showcase audiobook covers — keep for marketing; strip or regenerate for strict Findaway/ACX art checks.

---

## Files touched by this audit work

- `scripts/release/build_epub.py` — embed normalization, `--raw-cover`, metadata wording.
- `scripts/audiobook/generate_showcase_bundle.py` — manifest fields.
- `docs/EBOOK_PIPELINE_COMPLETE_GUIDE.md`, `docs/AUDIOBOOK_PIPELINE_COMPLETE_GUIDE.md`, `docs/DOCS_INDEX.md` — cross-links and operator notes.
- `artifacts/release/COVER_PACKAGING_PLATFORM_AUDIT_2026_04_10.md` — this document.

---

## CLOSEOUT_RECEIPT (audit lane)

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Research + Pearl_Dev + Pearl_PM
TASK:           Ebook + audiobook cover packaging audit (platform truth vs repo)
COMMIT_SHA:     no commits (working tree changes only unless owner commits)
FILES_WRITTEN:  artifacts/release/COVER_PACKAGING_PLATFORM_AUDIT_2026_04_10.md; scripts/release/build_epub.py; scripts/audiobook/generate_showcase_bundle.py; docs/EBOOK_PIPELINE_COMPLETE_GUIDE.md; docs/AUDIOBOOK_PIPELINE_COMPLETE_GUIDE.md; docs/DOCS_INDEX.md
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md; docs/PEARL_ARCHITECT_STATE.md; artifacts/coordination/ACTIVE_PROJECTS.tsv; ACTIVE_WORKSTREAMS.tsv; SUBSYSTEM_AUTHORITY_MAP.tsv; config/pipeline_registry.yaml; docs/EBOOK_PIPELINE_COMPLETE_GUIDE.md; docs/AUDIOBOOK_PIPELINE_COMPLETE_GUIDE.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; docs/PODCAST_PIPELINE_COMPLETE_GUIDE.md; scripts/run_pipeline.py; scripts/release/build_epub.py; scripts/audiobook/generate_showcase_bundle.py; scripts/video/render_audiobook.py; scripts/image_generation/generate_bestseller_covers.py; config/tts/brand_narrator_voice_map.yaml; artifacts/coordination/FUNNEL_PIPELINE_MERGE_CLOSEOUT_2026_04_10.md; official KDP/Apple/Google/Kobo/INaudio pages cited above
STATUS:         completed
HANDOFF_TO:     none
NEXT_ACTION:    Optional — re-run `python3 scripts/release/build_epub.py --batch` to refresh committed EPUBs; consider 1920×2560 Kobo storefront export and ACX JPG 2400 exporter if automating further
```
