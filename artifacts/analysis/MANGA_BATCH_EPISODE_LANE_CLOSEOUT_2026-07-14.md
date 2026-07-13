# Manga Batch Episode Lane Closeout

- implementation=`scripts/manga/run_episode_production.py`
- emits `episode_manifest.json`, `panel_status.tsv`, `gate_summary.json`.
- synthetic tests run without live GPU and record selected candidate, removed pixels, gate status, and final image.
- final page/webtoon composition remains dependent on the canonical full pipeline.
- manga-batch-episode-lane=green
- batch-panel-count-tested=1
- live-gpu-required-for-ci=no
- overall-manga-green=NOT_PROVEN
