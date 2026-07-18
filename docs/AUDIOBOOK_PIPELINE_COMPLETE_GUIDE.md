# Pearl Prime — Audiobook showcase pipeline (complete operator guide)

**Script:** `scripts/audiobook/generate_showcase_bundle.py`  
**Registry:** `config/pipeline_registry.yaml` → `pipelines.audiobook`

This path is optimized for **Pearl Star** operation (Qwen + CosyVoice2) as documented in the script header.

---

## Before you start

1. `python3 scripts/pipeline/create_job.py --pipeline audiobook --teacher … --topic … --brand … --locale … --workspace artifacts/audiobook_samples`
2. `python3 scripts/pipeline/acknowledge_guide.py --workspace artifacts/audiobook_samples`
3. Run subcommands: `prose`, `tts`, `covers`, `manifest`, or `all`.

---

## Stages (job tracking)

| Stage | Command | Output |
|-------|---------|--------|
| prose_gen | `… prose` | `artifacts/audiobook_samples/_prose/` |
| tts_render | `… tts` | `*_ch1.mp3` |
| cover_gen | `… covers` | cover PNGs |
| manifest | `… manifest` | `manifest.json` |
| distribute | investor/sizzle helpers | clips under `public/` (when run) |

Optional video path: `scripts/video/render_audiobook.py` (not wired to job stages by default).

---

## Voice map

Use **`config/tts/brand_narrator_voice_map.yaml`** for brand/locale → voice.  
Showcase script uses **CosyVoice2** presets from `generate_showcase_bundle.py` rows.

---

## Audio standards

- **−16 LUFS** integrated loudness  
- **−1.0 dBTP** true peak  
- ID3 / metadata where implemented in render stack

---

## Common mistakes

- Expecting **ElevenLabs** in this showcase script — it is intentionally Pearl Star / CosyVoice2.
- Running **`tts`** before **`prose`** without existing text files.
- Forgetting **`--workspace`** — job enforcement will refuse to run.

---

## Example

```bash
PYTHONPATH=. python3 scripts/audiobook/generate_showcase_bundle.py all \
  --workspace artifacts/audiobook_samples
```

Use `--no-job-check` only for CI smoke tests.

---

## Cover packaging (audiobook ≠ ebook)

- **`covers` / `covers-catalog`:** Writes **square** `cover_*_audiobook.png` (3200×3200) and portrait **`cover_*_ebook.png` (1600×2560)** under `brand-wizard-app/public/assets/covers/audiobook/` — distinct roles; do not substitute one for the other.
- **Manifest:** `manifest.json` includes `cover_audiobook_rel`, `cover_ebook_storefront_rel`, and `cover_role_notes` for upload routing.
- **Distributors:** Google Play audiobooks want 1:1 covers (2400² recommended; min 1024). Voices by INaudio / Findaway-style specs require **square**, **minimum 2400×2400**, no letterboxing ([Cover art technical requirements](https://voicessupport.inaudio.com/en/articles/3219584)). ACX/Audible expectations are summarized in Amazon’s [Official Audible Cover Art Requirements (PDF)](https://images-na.ssl-images-amazon.com/images/G/01/Audible/en_US/acx/pdf/OfficialAudibleCover-ArtRequirements.pdf) — typically **2400×2400** RGB **JPG**; export from our PNG master as needed.
- **Showcase badge:** Generated audiobook covers include an “AUDIOBOOK” ribbon for internal/teach marketing. Some distributors’ art rules discourage format callouts on cover art; use an unbadged variant for those uploads (manual or future script flag).
- Canonical matrix: [artifacts/release/COVER_PACKAGING_PLATFORM_AUDIT_2026_04_10.md](../artifacts/release/COVER_PACKAGING_PLATFORM_AUDIT_2026_04_10.md).
