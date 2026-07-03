#!/usr/bin/env bash
# Exact resume commands for replacing the INTERIM layers in
# demo_alarm_metaphor_6p with REAL banked renders, once Pearl Star is
# reachable again (it was unreachable 2026-07-03: SSH timeout to
# 100.92.68.74, ComfyUI :8188 no response, tailscale ping no reply).
#
# GPU priority: the CJK atom lane holds priority (OPD-20260629-003).
# Submit these as a bounded LOW-priority batch (~8 images, well under the
# 2-4 GPU-hour pilot envelope of Q-MANGA-03). Do NOT preempt.
#
# RAP: queue-first via pscli/enqueue_panel_job is MANDATORY. Never call
# ComfyUI directly.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# 0. Preflight: queue must be RUNNING, not PAUSED (RAP step 1)
ssh ahjan108@100.92.68.74 'set -a; . /etc/pearl-star/queue.env; set +a; ~/phoenix_omega/scripts/pearl_star/bin/pscli status'

# 1. L3 kettle — object_inventory kettle × on_burner_boiling (spec §4.4:
#    pure-white backdrop, rendered BIG, margin 10%)
PYTHONPATH=. python3 - <<'PY'
from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job
import yaml
inv = yaml.safe_load(open("config/source_of_truth/manga_profiles/series/stillness_en_01.object_inventory.yaml"))
kettle = next(o for o in inv["objects"] if o["object_id"] == "kettle")
prompt = ("Matte ceramic kettle, warm cream glaze, simple handle, curved spout, "
          + kettle["prompt_template_extras"]["on_burner_boiling"]
          + ", rendered LARGE filling 80% of frame, pure white backdrop, "
          "soft pen-and-ink linework, watercolor wash, iyashikei register")
enqueue_panel_job(task="t2i_qwen_image", prompt=prompt,
                  negative="people, person, hands, text, watermark, busy background",
                  width=1080, height=1920,
                  out_path="artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/image_bank/L3/kettle_on_burner_boiling.png")
PY

# 2. L3 cup — states empty/half/full (three cached variants per inventory)
for STATE in empty half full; do
PYTHONPATH=. STATE=$STATE python3 - <<'PY'
import os, yaml
from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job
state = os.environ["STATE"]
inv = yaml.safe_load(open("config/source_of_truth/manga_profiles/series/stillness_en_01.object_inventory.yaml"))
cup = next(o for o in inv["objects"] if o["object_id"] == "cup")
prompt = (cup["description"] + ", " + cup["prompt_template_extras"][state]
          + ", rendered LARGE filling 80% of frame, pure white backdrop, "
          "soft pen-and-ink linework, watercolor wash, iyashikei register")
enqueue_panel_job(task="t2i_qwen_image", prompt=prompt,
                  negative="people, person, hands, text, watermark",
                  width=1080, height=1920,
                  out_path=f"artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/image_bank/L3/cup_{state}.png")
PY
done

# 3. L1 wall alarm — mid-distance anchor (spec §4.2: 15% margin, white backdrop)
PYTHONPATH=. python3 - <<'PY'
from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job
enqueue_panel_job(task="t2i_qwen_image",
                  prompt=("Round wall-mounted smoke alarm, soft green LED ring idle state, "
                          "matte white shell, rendered LARGE centered, pure white backdrop, "
                          "soft pen-and-ink linework, iyashikei watercolor register"),
                  negative="people, text, watermark, wall, ceiling, background detail",
                  width=1080, height=1080,
                  out_path="artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/image_bank/L1/wall_alarm_green_idle.png")
PY

# 4. L4 steam — atmospheric overlay (spec §4.5: pure BLACK backdrop for
#    light effects; composited with screen blend)
PYTHONPATH=. python3 - <<'PY'
from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job
enqueue_panel_job(task="t2i_qwen_image",
                  prompt=("Single rising steam plume, soft white wisps curling upward, "
                          "gentle undulation, pure black backdrop, no objects, no people"),
                  negative="kettle, cup, text, color, background",
                  width=1080, height=1920,
                  out_path="artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/image_bank/L4/steam_wisp_rising.png")
PY

# 5. After renders land: cut sprites (proper white-backdrop cutouts key
#    cleanly), re-run the assembly with the REAL asset paths swapped into
#    the manifest, and re-emit the provenance table (expect 0 INTERIM rows).
PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \
  --manifest artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembly_manifests/demo_alarm_metaphor_6p.yaml \
  --out-dir  artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/assembled/demo_alarm_metaphor_6p_real \
  --strip --bubbles --locale en_US
