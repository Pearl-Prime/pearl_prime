# Music bank: 400 bases → 24 DNA → R2

## 1) Generate 400 base tracks (Google Colab)

On your machine (repo root):

```bash
python3 scripts/music/export_musicgen_manifest.py
```

This writes `artifacts/music/musicgen_manifest.jsonl` (400 jobs).

In **Google Colab**:

1. Runtime → Change runtime type → **T4 GPU**.
2. Run: `!pip install -q audiocraft soundfile`
3. Upload `musicgen_manifest.jsonl` to the Colab working directory (or Drive and `cd` there).
4. Upload `scripts/music/musicgen_colab.py` **or** paste its contents into a cell.
5. Optional: `!apt-get install -qq ffmpeg` then set `os.environ["MUSICGEN_EXPORT_MP3"] = "1"` before running to emit MP3 as well.
6. Run the script. Expect long wall time (~15–30 s/track → on the order of **hours** for 400; split across sessions by truncating the JSONL).

Download `music_bank/base/` (zip `music_bank` in Colab).

Back in the repo:

```bash
mkdir -p assets/music_bank/base
# copy *.wav or *.mp3 from Colab into assets/music_bank/base/
python3 scripts/music/build_music_index.py --bank-dir assets/music_bank
```

## 2) Apply 24 brand DNA transforms (local FFmpeg)

Requires **ffmpeg** on PATH.

```bash
python3 scripts/music/apply_brand_dna_batch.py \
  --base-dir assets/music_bank/base \
  --output-dir assets/music_bank/by_brand
```

Optional smoke test:

```bash
python3 scripts/music/apply_brand_dna_batch.py --limit-tracks 2 --limit-brands 2
```

This applies pitch/tempo/EQ/reverb/stereo from `config/music/brand_music_dna.yaml`. YAML *texture_overlay* files are **not** mixed unless you add a separate texture pipeline.

## 3) Upload to Cloudflare R2 (~5.4 GB)

```bash
pip install boto3
export R2_ACCOUNT_ID=...
export R2_ACCESS_KEY_ID=...
export R2_SECRET_ACCESS_KEY=...
export R2_BUCKET=...
export R2_PREFIX=music_bank/v1/

python3 scripts/music/upload_music_bank_r2.py --local-dir assets/music_bank/by_brand
```

Dry run first:

```bash
python3 scripts/music/upload_music_bank_r2.py --local-dir assets/music_bank/by_brand --dry-run
```

Register env names in `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` when you finalize operator secrets.

## Related

- Spec: `artifacts/research/therapeutic_music_bank_system_2026_04_06.md`
- Prompts: `config/music/therapeutic_music_prompts.yaml`
- DNA: `config/music/brand_music_dna.yaml`
- Video selection: `scripts/music/select_and_edit.py`
